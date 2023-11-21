from typing import List, Dict
from enum import Enum, unique

from XAgent.utils import RequiredAbilities
from XAgent.data_structure.node import Node
from XAgent.message_history import Message


class SummarizationNode(Node):
    """Class to represent nodes in the summarization tree.

    Inherits from the Node class defined in XAgent.data_structure.node.

    Attributes:
        father (SummarizationNode): Parent SummarizationNode.
        children (List[SummarizationNode]): List of child SummarizationNodes.
        message (Message): Message associated with this node.
        summarization_from_root_to_here: Summary from root node to this node.
    """
    def __init__(self):
        self.father: SummarizationNode = None
        self.children: List[SummarizationNode] = []

        self.message: Message = None

        self.summarization_from_root_to_here = None

    @classmethod
    def add_father_child_relation(cls, father, child):
        """Adds relation between father SummarizationNode and child SummarizationNode.

        Args:
            father (SummarizationNode): Parent node.
            child (SummarizationNode): Child node to be added to the parent node's children list.

        Raises:
            AssertionError: If the child node is already in the father's children list.
        """
        assert child not in father.children
        father.children.append(child)
        child.father = father


@unique
class SummarizationTreeQueryResult(Enum):
    """Enumeration for possible results when querying the summarization tree."""
    have_summary = 0
    not_in_tree = 1
    in_tree_but_no_summary = 2


class SummarizationTrieTree:
    """Class to represent the Summarization Trie Tree. The tree is used to generate summaries.

    Attributes:
        root (SummarizationNode): Root node of the tree.
        config: Configuration data for the tree.
    """
    def __init__(self, config):
        self.root = SummarizationNode()
        self.config = config

    def query(self, message_list: List[Message]) -> SummarizationTreeQueryResult:
        """Queries the tree with the given list of messages.

        Args:
            message_list (List[Message]): The list of messages for the tree query.

        Returns:
            SummarizationTreeQueryResult: The state of summary related to the query.
            SummarizationNode: If the list of messages is in the tree, returns the node where the search ended.
        """
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


    def insert(self, message_list):
        """Inserts a list of messages into the trie tree.

        Args:
            message_list (List[Message]): List of messages to be inserted into the tree.

        Returns:
            SummarizationNode: Returns the end node after insertion.
        """

    @classmethod
    def get_summarzation_message_all(cls, father_summarize_node: SummarizationNode, message_list: List[Message]) -> List[Message]:
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


    def generate_summary(self, message_list, recursive_mode=True, agent_dispatcher=None):
        """Generates a summary for the given list of messages.

        Args:
            message_list (List[Message]): List of messages to be summarized.
            recursive_mode (bool): Flag indicating if recursive mode summarization is required.
            
        Returns:
            str: The new summarized content text.
        """
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