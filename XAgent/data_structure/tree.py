from XAgent.data_structure.node import ToolNode


class TaskSearchTree:
    def __init__(self):
        self.root: ToolNode = ToolNode()
        self.root.expand_num = 0
        self.now_expand_num = 1

    def get_depth(self):
        return self.root.get_depth()

    def get_subtree_size(self):
        return self.root.get_subtree_size()

    def make_father_relation(self, father, child):
        child.expand_num = self.now_expand_num
        self.now_expand_num += 1

        child.father = father
        father.children.append(child)
