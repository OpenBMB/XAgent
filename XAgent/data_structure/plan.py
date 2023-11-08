from typing import List, Optional
from XAgent.utils import TaskSaveItem, TaskStatusCode
from XAgent.data_structure.node import ToolNode

class Plan():
    """Class representing a task plan.

    Attributes:
        father (Optional[Plan]): Parent task plan.
        children (List[Plan]): List of child task plans.
        data (TaskSaveItem): Data items related to the task plan.
        process_node (ToolNode): Node responsible for the task plan processing.
    """
    
    def __init__(self, data: TaskSaveItem):
        """Initialises a Plan object.

        Args:
            data (TaskSaveItem): Data related to the task plan.
        """
        self.father: Optional[Plan] = None
        self.children: List[Plan] = []
        self.data: TaskSaveItem = data
        self.process_node: ToolNode = None 
    
    def to_json(self, posterior=True):
        """Converts Plan object to JSON.

        Args:
            posterior (bool): Determines whether the task's posterior data 
                              is also returned.

        Returns:
            root_json (dict): JSON format representation of the Plan object.
        """
        root_json = self.data.to_json(posterior=posterior)
        if self.process_node:
            root_json["submit_result"] = self.process_node.data["command"]["properties"]

        # if self.father != None:
        root_json["task_id"] = self.get_subtask_id(to_str=True)
        if len(self.children) > 0:
            root_json["subtask"] = [ subtask.to_json() for subtask in self.children]
        return root_json
    
    def get_subtask_id(self, to_str=False):
        """Gets the subtask ID.

        Args:
            to_str (bool): Determines if returned ID is string.

        Returns:
            subtask_id_list (list): List of subtask IDs.
        """
        subtask_id_list = self.get_subtask_id_list()
        if to_str:
            subtask_id_list = [str(cont) for cont in subtask_id_list]
            return ".".join(subtask_id_list)
        else:
            return subtask_id_list

    def get_subtask_id_list(self):
        """Gets the subtask ID list.

        Returns:
            Array of subtask IDs if father is not none else [1].
        """
        if self.father == None:
            return [1]
        fahter_subtask_id = self.father.get_subtask_id()
        child_id = self.father.children.index(self) + 1
        fahter_subtask_id.append(child_id)
        return fahter_subtask_id
    
    @classmethod
    def make_relation(cls, father, child):
        """Establishes a parent-child relationship between two plans.

        Args:
            father: Parent plan.
            child: Child plan.
        """
        father.children.append(child)
        child.father = father

    def get_root(self):
        """Fetches the root of the Plan tree.

        Returns:
            Root Plan object.
        """
        if self.father == None:
            return self
        return self.father.get_root()

    def get_depth(self):
        """Returns the depth of the Plan tree.

        Returns:
            Tree depth as an integer.
        """
        if self.father == None:
            return 1
        return 1 + self.father.get_depth()

    @classmethod
    def get_inorder_travel(cls, now_plan):
        """Performs an inorder traversal of the plan tree.

        Args:
            now_plan: Current plan in the tree.

        Returns:
            All plans in the tree in inorder.
        """
        result_list = [now_plan]
        for child in now_plan.children:
            result_list.extend(Plan.get_inorder_travel(child))
        return result_list

    @classmethod
    def pop_next_subtask(cls, now_plan):
        """Fetches the next subtask in the queue.

        Args:
            now_plan: Current plan in the tree.

        Returns:
            Next subtask in the queue.
        """
        root_plan = now_plan.get_root()
        all_plans = Plan.get_inorder_travel(root_plan)
        order_id = all_plans.index(now_plan)
        for subtask in all_plans[order_id + 1:]:
            if subtask.data.status == TaskStatusCode.TODO:
                return subtask
        return None

    @classmethod
    def get_remaining_subtask(cls, now_plan):
        """Gets all remaining subtasks from a given point.

        Args:
            now_plan: Current plan in the tree.

        Returns:
            Array of all remaining subtasks.
        """
        root_plan = now_plan.get_root()
        all_plans = Plan.get_inorder_travel(root_plan)
        order_id = all_plans.index(now_plan)
        return all_plans[order_id:]