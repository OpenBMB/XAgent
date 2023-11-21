"""
ENVS
"""
import os

from dotenv import dotenv_values

config = dotenv_values(".env")


class XAgentServerEnv:
    """
    XAgentServer environment variables
    if you change value of the environment variable, you need to restart 
    the XAgentServer by running the following command:
    `python start_server.py`
    or start a unicorn server by yourself
    """
    app = "app:app"
    prod: bool = config.get("PROD", "False").lower() == "true"
    base_dir = "XAgentServer"
    use_redis: bool = False
    recorder_root_dir = "running_records"
    # you can set default_login with True,
    # use the default user "admin" with token "xagent-admin" to login,
    default_login: bool = True
    # only one XAgentServer can be set to check whether the interaction is running.
    check_running: bool = False
    host = "0.0.0.0"
    port = 8090
    debug = True
    reload = True
    workers = 1
    share_url = "https://x-agent.net/api/conv/community"

    class DB:
        """
        database config
        """
        use_db = True
        db_url = "mysql+pymysql://root:xagent@localhost:3306/xagent"

    class Redis:
        """
        redis config
        """
        use_redis = False
        redis_url = "redis://localhost"
        redis_host = "localhost"
        redis_port = 6379
        redis_db = 0
        redis_password = "xagent"

    # if you want to use email to send message,
    # you can set send_email to True and set
    # email_host,
    # email_port,
    # email_user,
    # email_password,
    # auth_server
    class Email:
        """
        email config
        """
        send_email = False
        email_host = ""
        email_port = 465
        email_user = ""
        email_password = ""
        auth_server = ""

    # if you want to use upload function,
    # you can set upload_dir to the path of the upload directory
    # and set upload_allowed_types of the allowed types
    class Upload:
        """
        upload config
        """
        upload_dir = "XAgentServer/localstorage/upload"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        upload_allowed_types = ["image/png", "image/jpeg",
                                "image/gif", "text/plain",
                                "application/msword", "pdf",
                                "txt", "pptx", "xlsx",
                                "doc", "ppt", "xls",
                                "zip", "rar", "tar",
                                "gz", "7z", "bz2",
                                "tgz", "tbz2", "tar.gz",
                                "tar.bz2"]


if os.path.exists("XAgentServer/application/core/prod_server_envs.py") and XAgentServerEnv.prod:
    from XAgentServer.application.core.prod_server_envs import XAgentServerEnv
