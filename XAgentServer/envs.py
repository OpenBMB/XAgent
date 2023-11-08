import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))



class XAgentServerEnv:
    """
    XAgentServer environment variables. The change of these environment variables need to re-start the XAgentServer.

    Attributes:
        app (str): App's entry point.
        prod (bool): When True, it implies that it's a production environment.
        base_dir (str): XAgentServer's working directory.
        use_redis (bool): When True, Redis will be used for caching.
        recorder_root_dir (str): Directory where running logs will be stored.
        default_login (bool): When True, the default user admin is allowed to login using the token xagent-admin.
        check_running (bool): When set to True, the XAgentServer checks if interactions are already running in
                               another XAgentServer instance.
        host (str): IP address where the XAgentServer hosts its services.
        port (int): Port number where the XAgentServer hosts its services.
        debug (bool): When True, the XAgentServer will run in debugging mode.
        reload (bool): When True, the XAgentServer will reload modules for every request.
        workers (int): Number of concurrent workers for the XAgentServer.
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
        """
        DataBase configurations for XAgentServer.

        Attributes:
            use_db (bool): When True, the database will be used for persistent storage.
            db_type (str): Type of the database to be used. It can be one of file, sqlite, mysql, postgresql.
            db_url (str or dict): Database URL for connection. The content varies according to the db_type.
        """
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
        """
        Redis configurations for XAgentServer.

        Attributes:
            use_redis (bool): When True, Redis is used for caching.
            redis_url (str): URL of the Redis Server.
            redis_host (str): Hostname of the Redis Server.
            redis_port (int): Port number at which the Redis Server is hosted.
            redis_db (int): The database to connect to on the Redis Server.
            redis_password (str): The password to authenticate the connection to the Redis database.
        """
        use_redis = False
        redis_url = "redis://localhost"
        redis_host = "localhost"
        redis_port = 6379
        redis_db = 0
        redis_password = None

    # if you want to use email to send message, you can set send_email to True and set email_host, email_port, email_user, email_password, auth_server
    class Email:
        """
        Email configurations for XAgentServer.

        Attributes:
            send_email (bool): When True, the Email service can be used for sending messages.
            email_host (str): The hostname of the email server.
            email_port (int): The port number of the email server.
            email_user (str): The username for the email server 
            email_password (str): The password to authenticate the user on the email server.
            auth_server (str): The authorization server for the email server.
        """
        send_email = False
        email_host = ""
        email_port = 465
        email_user = ""
        email_password = ""
        auth_server = ""

    # if you want to use upload function, you can set upload_dir to the path of the upload directory and set upload_allowed_types to the allowed types
    class Upload:
        """
        Upload configurations for XAgentServer.

        Attributes:
            upload_dir (str): Directory where the files will be uploaded.
            upload_allowed_types (list): List of allowed MIME types for upload.
        """
        upload_dir = "XAgentServer/localstorage/upload"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        upload_allowed_types = ["image/png", "image/jpeg", "image/gif", "text/plain",
                                "application/msword", "pdf", "txt", "pptx", "xlsx", "doc", "ppt", "xls"]


if os.path.exists("XAgentServer/prod_server_envs.py") and XAgentServerEnv.prod:
    from XAgentServer.prod_server_envs import XAgentServerEnv