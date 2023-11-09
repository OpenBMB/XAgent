from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from typing import List, Literal, TypedDict

from XAgent.logs import logger


MessageRole = Literal["system", "user", "assistant","function"]
MessageType = Literal["ai_response", "action_result"]


class MessageDict(TypedDict):
    """
    Typed dictionary to keep track of message attributes.

    Attributes:
        role (MessageRole): Source of the message. Can be either 'system', 'user', 'assistant', or 'function'.
        content (str): The message content.
        function_call (dict): Callable method.
    """

    role: MessageRole
    content: str
    function_call: dict

@dataclass
class Message:
    """OpenAI Message class.

    A class representing a message from an agent, a user, or a system function.

    Attributes:
        role (MessageRole): Source of the message, can be either 'system', 'user', 'assistant', or 'function'.
        content (str): The actual content of the message.
        type (MessageType): The type of message, either 'ai_response' for AI dialogue messages or 'action_result' for results of API calls.
        function_call (dict): A dictionary representing the method invocation in programmable API calls.
    """

    role: MessageRole
    content: str
    type: MessageType | None = None
    function_call: dict | None = None

    def raw(self) -> MessageDict:
        """Extracts raw content of the message, stripping away other metadata.

        Returns:
            MessageDict: Dictionary containing 'role' and 'content'.
        """
        data = {"role": self.role, "content": self.content}
        if self.function_call != None:
            data["function_call"] = self.function_call
        return data
        
    def to_json(self):
        """Convert the message into JSON format.

        Returns:
            MessageDict: JSON representation of the message.
        """
        return self.raw()

    @classmethod
    def equal(cls, a: Message, b: Message):
        """Checks if two messages are equal by comparing all their attributes.

        Args:
            a (Message): first message to be compared.
            b (Message): second message to be compared.

        Returns:
            bool: Returns True if both messages are equal in all their attributes; False otherwise.
        """
        if a.role != b.role:
            return False
        if a.content != b.content:
            return False
        if a.type != b.type:
            return False
        if a.function_call != b.function_call:
            return False
        return True

@dataclass
class ModelInfo:
    """Data class to store model information.

    Attributes:
        name (str): Model name
        prompt_token_cost (float): Token cost per prompt
        completion_token_cost (float): Token cost per completion
        max_tokens (int): Maximum tokens that can be generated
    """

    name: str
    prompt_token_cost: float
    completion_token_cost: float
    max_tokens: int


@dataclass
class ChatModelInfo(ModelInfo):
    """Data class to store chat model information."""


@dataclass
class TextModelInfo(ModelInfo):
    """Data class to store text generation model information."""


@dataclass
class EmbeddingModelInfo(ModelInfo):
    """Data class to store embedding model information.

    Attributes:
        embedding_dimensions (int): Number of dimensions in the embedding model.
    """

    embedding_dimensions: int


@dataclass
class MessageHistory:
    """Data class to store the history of messages.

    Contains methods to add, retrieve, trim the stored messages.

    Attributes:
        messages (list[Message]): List of messages in order of their creation.
        summary (str): String representing the summary of the conversation/history.
        last_trimmed_index (int): The index of the last erased message from the history.
    """

    messages: list[Message] = field(default_factory=list)
    summary: str = "I was created"

    last_trimmed_index: int = 0

    def __getitem__(self, i: int):
        """Enables accessing messages by their index.

        Args:
            i (int): Index of the message in the messages list.

        Returns:
            Message: Message at index i in the messages list.
        """
        return self.messages[i]

    def __iter__(self):
        """Returns an iterator over the messages list.

        Returns:
            iterator: An iterator over the messages list.
        """
        return iter(self.messages)

    def __len__(self):
        """Returns the count of messages in the messages list.

        Returns:
            int: Total number of messages in the messages list.
        """
        return len(self.messages)

    def add(
        self,
        role: MessageRole,
        content: str,
        type: MessageType | None = None,
        function_call: str | None = None,
    ):
        """Adds a new message to the messages list.

        Args:
            role (MessageRole): Source of the message, either 'system', 'user', 'assistant', or 'function'.
            content (str): Actual content of the message.
            type (MessageType): Type of the message, 'ai_response' for AI dialogue messages or 'action_result' for results of API calls. Default to None if not specified.
            function_call (str): A dictionary representing the method invocation in programmable API calls. Default to None if not specified.

        Returns:
            None
        """
        if function_call == None:
            message = Message(role, content, type)
        else:
            message = Message(role, content, type, function_call)
        return self.append(message)

    def append(self, message: Message):
        """Appends a new message to the messages list.

        Args:
            message (Message): Message to append to the list.

        Returns:
            None.
        """
        return self.messages.append(message)

    def trim_messages(
        self,
        current_message_chain: list[Message],
    ) -> tuple[Message, list[Message]]:
        """
        Returns a list of trimmed messages: messages which are in the message history
        but not in current_message_chain.

        Args:
            current_message_chain (list[Message]): The messages currently in the context.

        Returns:
            Message: A message with the new running summary after adding the trimmed messages.
            list[Message]: A list of messages that are in full_message_history with an index higher than last_trimmed_index and absent from current_message_chain.
        """
        # Select messages in full_message_history with an index higher than last_trimmed_index
        new_messages = [
            msg for i, msg in enumerate(self) if i > self.last_trimmed_index
        ]

        # Remove messages that are already present in current_message_chain
        new_messages_not_in_chain = [
            msg for msg in new_messages if msg not in current_message_chain
        ]

        if not new_messages_not_in_chain:
            return self.summary_message(), []

        new_summary_message = self.update_running_summary(
            new_events=new_messages_not_in_chain
        )

        # Find the index of the last message processed
        last_message = new_messages_not_in_chain[-1]
        self.last_trimmed_index = self.messages.index(last_message)

        return new_summary_message, new_messages_not_in_chain

    def per_cycle(self, messages: list[Message] | None = None):
        """
        This method yields user, ai, and result messages from the conversation cycle.

        Args:
            messages (list[Message]): The messages currently in the context. If None, uses self.messages.

        Yields:
            tuple: A tuple containing:
                - user_message (Message): a message containing user input
                - ai_message (Message): a message from the AI containing a proposed action
                - result_message (Message): the message containing the result of the AI's proposed action
        """
        messages = messages or self.messages
        for i in range(0, len(messages) - 1):

            ai_message = messages[i]

            if ai_message.type != "ai_response":
                continue

            user_message = (
                messages[i - 1] if i > 0 and messages[i - 1].role == "user" else None
            )
            result_message = messages[i + 1]
            try:
                assert result_message.type == "action_result"

                yield user_message, ai_message, result_message
            except AssertionError as err:
                logger.debug(
                    f"Invalid item in message history: {err}; Messages: {messages[i-1:i+2]}"
                )

    def summary_message(self) -> Message:
        """Build summary message from the current summary.

        Returns:
            Message: A system message containing the current summary
        """
        return Message(
            "system",
            f"This reminds you of these events from your past: \n{self.summary}",
        )

    def update_running_summary(self, new_events: list[Message]) -> Message:
        """
        This function takes a list of dictionaries representing new events and combines them with the current summary,
        focusing on key and potentially important information to remember. The updated summary is returned in a message
        formatted in the 1st person past tense.

        Args:
            new_events (List[Dict]): A list of dictionaries containing the latest events to be added to the summary.

        Returns:
            str: A message containing the updated summary of actions, formatted in the 1st person past tense.

        Example:
            new_events = [{"event": "entered the kitchen."}, {"event": "found a scrawled note with the number 7"}]
            update_running_summary(new_events)
            # Returns: "This reminds you of these events from your past: \nI entered the kitchen and found a scrawled note saying 7."
        """
        cfg = Config()

        if not new_events:
            return self.summary_message()

        # Create a copy of the new_events list to prevent modifying the original list
        new_events = copy.deepcopy(new_events)

        # Replace "assistant" with "you". This produces much better first person past tense results.
        for event in new_events:
            if event.role.lower() == "assistant":
                event.role = "you"

                # Remove "thoughts" dictionary from "content"
                try:
                    content_dict = json.loads(event.content)
                    if "thoughts" in content_dict:
                        del content_dict["thoughts"]
                    event.content = json.dumps(content_dict)
                except json.decoder.JSONDecodeError:
                    if cfg.debug_mode:
                        logger.error(f"Error: Invalid JSON: {event.content}\n")

            elif event.role.lower() == "system":
                event.role = "your computer"

            # Delete all user messages
            elif event.role == "user":
                new_events.remove(event)

        prompt = f'''Your task is to create a concise running summary of actions and information results in the provided text, focusing on key and potentially important information to remember.

You will receive the current summary and the your latest actions. Combine them, adding relevant key information from the latest development in 1st person past tense and keeping the summary concise.

Summary So Far:
"""
{self.summary}
"""

Latest Development:
"""
{new_events or "Nothing new happened."}
"""
'''

        prompt = ChatSequence.for_model(cfg.fast_llm_model, [Message("user", prompt)])
        self.agent.log_cycle_handler.log_cycle(
            self.agent.config.ai_name,
            self.agent.created_at,
            self.agent.cycle_count,
            prompt.raw(),
            PROMPT_SUMMARY_FILE_NAME,
        )

        self.summary = create_chat_completion(prompt)

        self.agent.log_cycle_handler.log_cycle(
            self.agent.config.ai_name,
            self.agent.created_at,
            self.agent.cycle_count,
            self.summary,
            SUMMARY_FILE_NAME,
        )

        return self.summary_message()