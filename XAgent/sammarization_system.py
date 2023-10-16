from typing import List, Dict
from enum import Enum, unique

from XAgent.utils import RequiredAbilities
from XAgent.global_vars import agent_dispatcher
from XAgent.data_structure.node import Node
from XAgent.message_history import Message

class SummarizationNode(Node):
    def __init__(self):
        self.father: SummarizationNode = None
        self.children: List[SummarizationNode] = []

        self.message: Message = None

        self.summarization_from_root_to_here = None

    @classmethod
    def add_father_child_relation(cls, father, child):
        assert child not in father.children
        father.children.append(child)
        child.father = father

@unique
class SummarizationTreeQueryResult(Enum):
    have_summary = 0
    not_in_tree = 1
    in_tree_but_no_summary = 2


class SummarizationTrieTree:
    def __init__(self, config):
        self.root = SummarizationNode()
        self.config = config

    def query(self, message_list: List[Message]) -> SummarizationTreeQueryResult:
        now_node = self.root

        now_position = 0
        while now_position < len(message_list):
            now_message = message_list[now_position]
            find = False
            for child in now_node.children:
                if Message.equal(child.message, now_message):
                    find = True
                    now_node = child
                    break
            
            if find:
                now_position += 1
            else:
                return SummarizationTreeQueryResult.not_in_tree, now_node
        
        if now_node.summarzation_from_root_to_here:
            return SummarizationTreeQueryResult.have_summary, now_node
        else:
            return SummarizationTreeQueryResult.in_tree_but_no_summary, now_node
        

    def insert(self,message_list):
        now_node = self.root

        now_position = 0
        while now_position < len(message_list):
            now_message = message_list[now_position]
            find = False
            for child in now_node.children:
                if Message.equal(child.message, now_message):
                    find = True
                    now_node = child
                    break
            
            if find:
                now_position += 1
            else:
                break

        assert now_position < len(message_list)


        for i in range(now_position, len(message_list)):
            new_node = SummarizationNode()
            new_node.message = message_list[i]
            SummarizationNode.add_father_child_relation(now_node,new_node)
            now_node = new_node

        return now_node

    @classmethod
    def get_summarzation_message_all(cls, father_summarize_node: SummarizationNode, message_list: List[Message]):
        system_prompt = f'''Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.

        You will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.

        Latest Development:
        """
        {[message.content for message in message_list] or "Nothing new happened."}
        """
        '''

        message_list = [Message("system",system_prompt )]

        return message_list



    @classmethod
    def get_summarzation_message_recursive(cls, father_summarize_node: SummarizationNode, new_message: Message):
        system_prompt = f'''Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.

        You will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.

        Summary So Far:
        """
        {father_summarize_node.summarization_from_root_to_here}
        """

        Latest Development:
        """
        {[message.content for message in new_message] or "Nothing new happened."}
        """
        '''

        message_list = [Message("system",system_prompt )]

        return message_list


    def generate_summary(self, message_list, recursive_mode=True):
        status_code, summarize_node = self.query(message_list)
        assert status_code != SummarizationTreeQueryResult.have_summary
        if recursive_mode:
            status_code, summarize_node = self.query(message_list[:-1])
            assert status_code == SummarizationTreeQueryResult.have_summary

            summarize_message_list = self.get_summarzation_message_recursive(summarize_node, message_list[-1])
        else:
            
            if status_code == SummarizationTreeQueryResult.not_in_tree:
                summarize_node = self.insert(message_list)
            summarize_message_list = self.get_summarzation_message_all( summarize_node, message_list)


        # print(summarize_message_list)
        agent = agent_dispatcher.dispatch(
            RequiredAbilities.summarization, 
            "Summarize the given content"
        )

        _, new_message, _ = agent.parse(placeholders={
            "system": {
                "running_summary": summarize_node.summarization_from_root_to_here,
                "new_message": [message.content for message in message_list] or "Nothing new happened."
            }
        })

        new_summary = new_message["content"]

        summarize_node.summarization_from_root_to_here = new_summary

        return new_summary
        
            
summary_system = SummarizationTrieTree()
