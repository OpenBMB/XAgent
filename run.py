import asyncio
from copy import deepcopy
import os
import sys
import argparse

from XAgent.config import CONFIG, ARGS
from command import CommandLine, CommandLineParam


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str,
                        help="task description",required=False)
    parser.add_argument("--upload_files", nargs='+',
                        help="upload files")
    parser.add_argument("--model", type=str, default=None,)
    parser.add_argument("--mode", type=str, default="auto",
                        help="mode, only support auto and manual, if you choose manual, you need to press enter to continue in each step")
    parser.add_argument("--quiet", action="store_true",default=False)
    parser.add_argument("--config_file", type=str, default="assets/config.yml")
    
    parser.add_argument("--max_subtask_chain_length", type=int, default=30)
    parser.add_argument("--enable_ask_human_for_help", action="store_true",default=False)
    parser.add_argument("--max_plan_refine_chain_length", type=int, default=3)
    parser.add_argument("--max_plan_tree_depth", type=int, default=3)
    parser.add_argument("--max_plan_tree_width", type=int, default=7)
    parser.add_argument("--max_retry_times", type=int, default=3)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    
    os.environ['CONFIG_FILE'] = args.config_file
    if args.quiet:
        original_stdout = sys.stdout
        # from XAgentServer.running_recorder import recorder
        # sys.stdout = open(os.path.join(recorder.record_root_dir,"command_line.ansi"),"w")
    for key,value in vars(args).items():
        if value is not None:
            if key == 'model':
                ARGS['default_completion_kwargs'] = deepcopy(CONFIG['default_completion_kwargs'])
                ARGS['default_completion_kwargs']['model'] = value
            else:
                ARGS[key] = value
    if args.task is not None:
        task = args.task
    else:
        task = "I will have five friends coming to visit me this weekend, please find and recommend some restaurants for us."    
    param = CommandLineParam(
        task=task,
        upload_files=args.upload_files,
        role="Assistant",
        mode=args.mode,
    )
    cmd = CommandLine(
        args=param,
    )
    cmd.start()
    if args.quiet:
        sys.stdout.close()
        sys.stdout = original_stdout
    