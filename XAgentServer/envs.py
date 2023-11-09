import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))


class XAgentServerEnv:
    """
    XAgentServer environment variables
    if you change value of the environment variable, you need to restart the XAgentServer by running the following command:
    `python start_server.py`
    or start a unicorn server by yourself

    """

    app = "app:app"
    prod: bool = os.getenv("PROD", "False").lower() == "true"
    base_dir = "XAgentServer"
    use_redis: bool = False
    recorder_root_dir = "running_records"
    # you can set default_login with True to use the default user "admin" with token "xagent-admin" to login,
    default_login: bool = True
    # the parameter check_running is used to check whether the interaction is running,
    # if you want to connect more than one XAgentServer, you can set check_running to True,
    # in which case the XAgentServer will check whether the interaction is running in other XAgentServer
    check_running: bool = False
    host = "0.0.0.0"
    port = 8090
    debug = True
    reload = True
    workers = 1

    class DB:
        use_db = False
        # Optional["file", "sqlite", "mysql", "postgresql"]
        db_type = "file"
        if db_type == "file":
            # if you want to use file to store data, you can set db_url to {"users": "path/to/users.json", "interactions": "path/to/interaction.json", "parameter": "path/to/parameter.json"}
            db_url = {
                "users": "XAgentServer/localstorage/users/users.json",
                "interactions": "XAgentServer/localstorage/records/interaction.json",
                "parameter": "XAgentServer/localstorage/records/parameter.json",
            }
        else:
            if db_type == "sqlite":
                # if you want to use sqlite to store data, you can set db_url to "sqlite://{}", in which {} is the absolute path of the sqlite file
                db_url = "sqlite://"
            if db_type == "mysql":
                # if you want to use mysql to store data, you can set db_url to "mysql+pymysql://{}:{}@{}:{}/{}, in which {} is {db_user, db_password, db_host, db_port, db_name}
                db_url = "mysql+pymysql://"
            if db_type == "postgresql":
                # if you want to use postgresql to store data, you can set db_url to "postgresql://{}:{}@{}:{}/{}"
                db_url = ""

    class Redis:
        use_redis = False
        redis_url = "redis://localhost"
        redis_host = "localhost"
        redis_port = 6379
        redis_db = 0
        redis_password = None

    # if you want to use email to send message, you can set send_email to True and set email_host, email_port, email_user, email_password, auth_server
    class Email:
        send_email = False
        email_host = ""
        email_port = 465
        email_user = ""
        email_password = ""
        auth_server = ""

    # if you want to use upload function, you can set upload_dir to the path of the upload directory and set upload_allowed_types to the allowed types
    class Upload:
        upload_dir = "XAgentServer/localstorage/upload"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        upload_allowed_types = [
            "image/png",
            "image/jpeg",
            "image/gif",
            "text/plain",
            "application/msword",
            "pdf",
            "txt",
            "pptx",
            "xlsx",
            "doc",
            "ppt",
            "xls",
        ]


if os.path.exists("XAgentServer/prod_server_envs.py") and XAgentServerEnv.prod:
    from XAgentServer.prod_server_envs import XAgentServerEnv
