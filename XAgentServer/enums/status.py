"""XAgent Status Enum"""


class StatusEnum:
    """XAgent Status Enum
    """
    START = "start"
    SUBTASK = "subtask"
    REFINEMENT = "refinement"
    INNER = "inner"
    FINISHED = "finished"
    FAILED = "failed"
    SUBMIT = "subtask_submit"
    RUNNING = "running"
    ASK_FOR_HUMAN_HELP = "ask_for_human_help"
    CLOSED = "closed"
    