from typing import List, Optional
from XAgent.utils import TaskSaveItem, TaskStatusCode
from XAgent.data_structure.node import ToolNode

class Plan():
    def __init__(self, data: TaskSaveItem):
        self.father: Optional[Plan] = None
        self.children: List[Plan] = []
        self.data: TaskSaveItem = data
        self.process_node: ToolNode = None 
    
    def to_json(self, posterior=True):
        root_json = self.data.to_json(posterior=posterior)
        if self.process_node:
            root_json["submit_result"] = self.process_node.data["command"]["properties"]

        # if self.father != None:
        root_json["task_id"] = self.get_subtask_id(to_str=True)
        if len(self.children) > 0:
            root_json["subtask"] = [ subtask.to_json() for subtask in self.children]
        return root_json
    
    def get_subtask_id(self, to_str=False):
        subtask_id_list = self.get_subtask_id_list()
        if to_str:
            subtask_id_list = [str(cont) for cont in subtask_id_list]
            return ".".join(subtask_id_list)
        else:
            return subtask_id_list

    def get_subtask_id_list(self):
        if self.father == None:
            return [1]
        fahter_subtask_id = self.father.get_subtask_id()
        child_id = self.father.children.index(self) + 1
        fahter_subtask_id.append(child_id)
        return fahter_subtask_id
    
    @classmethod
    def make_relation(cls, father, child):
        father.children.append(child)
        child.father = father

    def get_root(self):
        if self.father == None:
            return self
        return self.father.get_root()

    def get_depth(self):
        if self.father == None:
            return 1
        return 1 + self.father.get_depth()

    @classmethod
    def get_inorder_travel(cls, now_plan):
        result_list = [now_plan]
        for child in now_plan.children:
            result_list.extend(Plan.get_inorder_travel(child))
        return result_list

    @classmethod
    def pop_next_subtask(cls, now_plan):

        root_plan = now_plan.get_root()
        all_plans = Plan.get_inorder_travel(root_plan)
        order_id = all_plans.index(now_plan)
        for subtask in all_plans[order_id + 1:]:
            if subtask.data.status == TaskStatusCode.TODO:
                return subtask
        return None

    @classmethod
    def get_remaining_subtask(cls, now_plan):
        root_plan = now_plan.get_root()
        all_plans = Plan.get_inorder_travel(root_plan)
        order_id = all_plans.index(now_plan)
        return all_plans[order_id:]