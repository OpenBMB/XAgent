import asyncio
from contextlib import contextmanager
import json
import os
import threading
import traceback
import uuid
from datetime import datetime
from typing import List

from colorama import Fore

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler


from XAgentServer.application.core.envs import XAgentServerEnv
from XAgentServer.database.connect import SessionLocal
from XAgentServer.enums.status import StatusEnum
from XAgentServer.exts.exception_ext import XAgentError
from XAgentServer.interaction import XAgentInteraction
from XAgentServer.loggers.logs import Logger
from XAgentServer.models.interaction import InteractionBase
from XAgentServer.models.parameter import InteractionParameter
from XAgentServer.models.raw import XAgentRaw
from XAgentServer.server import XAgentServer
from XAgentServer.application.cruds.interaction import InteractionCRUD
from XAgentServer.application.global_val import redis
from command_input import CommandLineInput


@contextmanager
def get_db():
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        

class CommandLineParam:
    """Command line parameters.
    
    Attributes:
            task: Task description.
            role: Role name (default is "Assistant").
            plan: List of steps to perform (default is empty list).
            upload_files: List of files to upload (default is empty list).
            download_files: List of files to download (default is empty list).
            record_dir: Directory to store records (default is `None`).
            mode: Run mode. Can be "auto" (default is "auto").
            max_wait_seconds: Maximum wait time in seconds (default is 600).
            description: Description of the interaction (default is "XAgent-Test").
            agent: Agent name (default is "XAgent").
    """
    def __init__(self,
                 task,
                role="Assistant",
                plan=[],
                upload_files: List[str] = [],
                download_files: List[str] = [],
                record_dir: str = None,
                mode: str = "auto",
                max_wait_seconds: int = 600,
                description: str = "XAgent-Test",
                agent: str = "XAgent",
                ):
        self.task = task
        self.plan = plan
        self.role = role
        self.upload_files = upload_files
        self.download_files = download_files
        self.record_dir = record_dir
        # auto is supported only in cmd
        self.mode = "auto"
        self.max_wait_seconds = max_wait_seconds
        self.description = description
        self.agent = agent


class CommandLine():
    """
    A command-line interface for interacting with XAgentServer.

    Attributes:
        env: An instance of the XAgentServer environment.
        client_id: A unique identifier for the client, generated as a hexadecimal UUID.
        date_str: The current date as a string in YYYY-MM-DD format.
        log_dir: The directory where the logs are stored.
        logger: An instance of the Logger used for logging interactions.
        interactionDB: A database interface for interacting with either a persistent
            database (SQLite, MySQL, PostgreSQL) or a local storage file, depending
            on the configuration of `env`.
    """

    def __init__(self, args: CommandLineParam = None):
        """
        Initialize the CommandLine instance.

        Args:
            args (CommandLineParam) : parameters.
            task is required,
            mode options: ["auto"]
        """

        self.args = args
        self.client_id = uuid.uuid4().hex
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_dir = os.path.join(os.path.join(XAgentServerEnv.base_dir, "localstorage",
                                    "interact_records"), self.date_str, self.client_id)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = Logger(log_dir=self.log_dir, log_file=f"interact.log")

        self.logger.typewriter_log(
            title=f"XAgentServer is running on cmd mode",
            title_color=Fore.RED)
        self.logger.info(title=f"XAgentServer log:",
                         title_color=Fore.RED, message=f"{self.log_dir}")
        self.interrupt = self.args.mode != "auto"
        self.init_conv_env()
        self.max_wait_seconds = self.args.max_wait_seconds
        self.scheduler = AsyncIOScheduler()
        self.input = None
        if self.interrupt:
            self.input = CommandLineInput(
                do_interrupt=True,
                max_wait_seconds=self.max_wait_seconds,
                logger=self.logger)

    def init_conv_env(self):
        """initialize the conversation environment, 
        Share the same database resource with webui.
        If you have initiated a session on the front end but it has not been executed, 
        this ID will be shared.
        """
        user_id = "guest"
        token = "xagent"
        description = self.args.description
        upload_files = self.args.upload_files
        record_dir = self.args.record_dir
        agent = self.args.agent
        goal = self.args.task
        mode = self.args.mode
        plan = self.args.plan

        with get_db() as db:
            interaction = InteractionCRUD.get_ready_interaction(
                db=db, user_id=user_id)
            self.continue_flag = True
            upload_files = upload_files if upload_files else []
            file_list = []
            for file in upload_files:
                file_list.append({
                    "uuid": file,
                    "name": file
                })
            if interaction is None:

                base = InteractionBase(interaction_id=self.client_id,
                                       user_id=user_id,
                                       create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       description=description,
                                       agent=agent,
                                       mode=mode,
                                       file_list=file_list,
                                       recorder_root_dir="",
                                       status="ready",
                                       message="ready...",
                                       current_step="-1",
                                       update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       call_method="cmd")
                InteractionCRUD.create_interaction(db=db, base=base)
            else:
                self.client_id = interaction.interaction_id
            
            parameter = InteractionParameter(
                interaction_id=self.client_id,
                parameter_id=uuid.uuid4().hex,
                args={
                    "goal": goal,
                    "plan": plan
                    },
            )
            InteractionCRUD.add_parameter(db=db, parameter=parameter)


    def run(self):
        """
        Runs the interaction with the XAgentServer with the provided arguments.
        """

        # Create a new raw data to record
        with get_db() as db:
            InteractionCRUD.insert_raw(db=db, process=XAgentRaw(
                interaction_id=self.client_id,
                node_id=uuid.uuid4().hex,
                status=StatusEnum.RUNNING,
                create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                current="",
                step=-1,
                data=None,
                file_list=[],
                do_interrupt=self.interrupt,
                wait_seconds=0,
                ask_for_human_help=False,
                is_human=True,
                human_data={"goal": self.args.task, "plan": self.args.plan},
                human_file_list=self.args.upload_files,
                is_send=True,
                is_receive=False,
                is_deleted=False
            ))
            redis.set_key(f"{self.client_id}_send", 1)
            
            parameter = InteractionCRUD.get_init_parameter(
                db=db, interaction_id=self.client_id)
        
        self.task_handler(parameter=parameter)

    def task_handler(self, parameter: InteractionParameter):
        """
        define a long task to run interaction

        Args:
            parameter (InteractionParameter): The parameter of interaction
        """

        try:
            current_step = uuid.uuid4().hex
            with get_db() as db:
                base = InteractionCRUD.get_interaction(db=db,
                                                    interaction_id=self.client_id)
                InteractionCRUD.update_interaction_status(db=db,
                                                        interaction_id=base.interaction_id,
                                                        status="running",
                                                        message="running",
                                                        current_step=current_step)

            # if mode is not auto, we will interrupt the interaction
            # and you can change the wait_seconds
            # default 10 min.
            interaction = XAgentInteraction(
                base=base,
                parameter=parameter,
                interrupt=base.mode != "auto",
                call_method="cmd")

            # Register logger, dbinto interaction
            interaction.resister_logger(self.logger)
            self.logger.info(
                f"Register logger into interaction of {base.interaction_id}, done!")

            interaction.register_db(db=db)
            self.logger.info(
                f"Register db into interaction of {base.interaction_id}, done!")
            # Create XAgentServer
            server = XAgentServer(logger=self.logger)
            self.logger.info(
                f"Register logger into XAgentServer of {base.interaction_id}, done!")
            self.logger.info(
                f"Start a new thread to run interaction of {base.interaction_id}, done!")
            # await server.interact(interaction=interaction)
            server.interact(interaction=interaction)
        except XAgentError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error in task_handler of {self.client_id}: {e}")
            with get_db() as db:
                InteractionCRUD.insert_error(
                    db=db, interaction_id=self.client_id, message=str(e))
                redis.set_key(self.client_id + "_send", 1)
                InteractionCRUD.update_interaction_status(db=db,
                                                        interaction_id=self.client_id,
                                                        status="failed",
                                                        message=str(e),
                                                        current_step=current_step)
        
    def start(self):

        self.run()


if __name__ == "__main__":
    import sys
    args = CommandLineParam()
    if len(sys.argv) >= 2:
        print(sys.argv[1])
        if len(sys.argv) >= 3:
            original_stdout = sys.stdout
            from XAgent.running_recorder import recorder
            sys.stdout = open(os.path.join(
                recorder.record_root_dir, "command_line.ansi"), "w", encoding="utf-8")

        args.task = sys.argv[1],
        args.role="Assistant",
        args.mode="auto",
        if len(sys.argv) >= 3:
            sys.stdout.close()
            sys.stdout = original_stdout

    else:
        args.task = "I will have five friends coming to visit me this weekend, please find and recommend some restaurants for us.",
        args.role="Assistant",
        args.mode="auto",
        
    cmd = CommandLine(XAgentServerEnv, args)
