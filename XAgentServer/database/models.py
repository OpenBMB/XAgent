"""SQLAlchemy models for XAgentServer"""
from sqlalchemy import JSON, Boolean, Column, Integer, String, Text
from XAgentServer.database.connect import Base


class User(Base):
    """XAgent Users"""
    __tablename__="users"

    id=Column(Integer,primary_key=True,index=True)
    user_id = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    token = Column(String(255))
    available = Column(Boolean, default=True)
    is_beta = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    corporation = Column(Text)
    industry = Column(Text)
    position = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))


class Interaction(Base):
    """XAgent Interactions"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(255))
    user_id = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))
    description = Column(Text)
    agent = Column(String(255))
    mode = Column(String(255))
    recorder_root_dir = Column(Text)
    file_list = Column(JSON)
    status = Column(String(255))
    message = Column(Text)
    current_step = Column(String(255))
    is_deleted = Column(Boolean, default=False)
    call_method = Column(String(255), default="web")


class Parameter(Base):
    """XAgent Parameters"""
    __tablename__ = "interaction_parameters"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(32), unique=True, index=True)
    parameter_id = Column(String(32))
    args = Column(JSON)


class SharedInteraction(Base):
    """Commnunity Shared Interactions"""
    __tablename__ = "shared_interactions"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(255))
    user_name = Column(String(255))
    create_time = Column(String(255))
    update_time = Column(String(255))
    description = Column(Text)
    agent = Column(String(255))
    mode = Column(String(255))
    is_deleted = Column(Boolean, default=False)
    star = Column(Integer, default=0)
    is_audit = Column(Boolean, default=False)


class Raw(Base):
    """Raw Data"""
    __tablename__ = "raw"
    # id/id
    id = Column(Integer, primary_key=True, index=True)
    # node_id
    node_id = Column(String(255))
    # 交互id/interaction_id
    interaction_id = Column(String(255))
    # 当前节点/current
    current = Column(String(128))
    # step/step
    step = Column(Integer, default=0)
    # 数据/agent data
    data = Column(JSON)
    # workspace文件列表/workspace file list
    file_list = Column(JSON)
    # 状态/status
    status = Column(String(20))
    # 是否中断/interrupt or not
    do_interrupt = Column(Boolean, default=False)
    # 已等待时间/wait seconds
    wait_seconds = Column(Integer, default=0)
    # 是否需要人工干预/ask for human help or not
    ask_for_human_help = Column(Boolean, default=False)
    # 创建时间/create time
    create_time = Column(String(255))
    # 更新时间/update time
    update_time = Column(String(255))
    # 是否删除/is deleted or not
    is_deleted = Column(Boolean, default=False)
    # 是否人工已经输入/has human input or not
    is_human = Column(Boolean, default=False)
    # 人工输入数据/human data
    human_data = Column(JSON)
    # 人工文件列表/agent file list
    human_file_list = Column(JSON)
    # 是否推送前端/has send to frontend or not
    is_send = Column(Boolean, default=False)
    # 是否接收前端消息/has receive message from frontend or not
    is_receive = Column(Boolean, default=False)
    # 是否包含png/has png or not
    include_pictures = Column(Boolean, default=False)


class RunningRecord(Base):
    """Running Record"""
    __tablename__ = "running_record"
    # id/id
    id = Column(Integer, primary_key=True, index=True)
    # record_id/record_id
    record_id = Column(String(255))
    # 当前节点/current
    current = Column(String(255))
    # 节点id/node_id
    node_id = Column(String(255))
    # 节点类型/node_type, options: [now_subtask_id, llm_input_pair, tool_server_pair, query, config]
    node_type = Column(String(255))
    # data/agent data
    data = Column(JSON)
    # 创建时间/create time
    create_time = Column(String(255))
    # 更新时间/update time
    update_time = Column(String(255))
    # 是否删除/is deleted or not
    is_deleted = Column(Boolean, default=False)
