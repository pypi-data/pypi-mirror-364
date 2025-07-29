import time
from typing import List, Optional
from rebel.models import (
    AssistantInput,
    AssistantOutput,
    Function,
    ToolCall,
    Message
)
from rebel.collector import APIClient


class OpenAIAPIClient(APIClient):
    """
    Alternative client that uses the OpenAI SDK directly 
    """
    def __init__(self, api_key: str, model: str, base_url: str):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def request(self, input: AssistantInput) -> AssistantOutput:
        start_time = time.time()
        actual_output = ""
        tools_called: List[ToolCall] = []
        context: List[str] = []
        
        # Convert messages to OpenAI format
        messages = []
        for message in input.messages:
            msg_dict = {
                "role": message.role.value,
                "content": message.content
            }
            
            if message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            if message.tool_call_id:
                msg_dict["tool_call_id"] = message.tool_call_id
                
            messages.append(msg_dict)
        
        # Prepare request parameters
        request_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **{k: v for k, v in input.api_params.items() if k != "model"}
        }
        
        try:
            stream = self.client.chat.completions.create(**request_params)
            
            current_tool_calls = {}
            
            for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    
                    # Handle content
                    if delta.content:
                        actual_output += delta.content
                    
                    # Handle tool calls
                    if delta.tool_calls:
                        for tc_delta in delta.tool_calls:
                            tc_index = tc_delta.index if hasattr(tc_delta, 'index') else 0
                            
                            if tc_index not in current_tool_calls:
                                current_tool_calls[tc_index] = {
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                }
                            
                            if tc_delta.id:
                                current_tool_calls[tc_index]["id"] = tc_delta.id
                            
                            if tc_delta.type:
                                current_tool_calls[tc_index]["type"] = tc_delta.type
                            
                            if tc_delta.function:
                                if tc_delta.function.name:
                                    current_tool_calls[tc_index]["function"]["name"] += tc_delta.function.name
                                if tc_delta.function.arguments:
                                    current_tool_calls[tc_index]["function"]["arguments"] += tc_delta.function.arguments
                    
                    # Check if tool calls are complete
                    if choice.finish_reason == "tool_calls" and current_tool_calls:
                        for tc_data in current_tool_calls.values():
                            if tc_data["function"]["name"]:
                                tools_called.append(
                                    ToolCall(
                                        id=tc_data["id"],
                                        type=tc_data["type"],
                                        function=Function(
                                            name=tc_data["function"]["name"],
                                            arguments=tc_data["function"]["arguments"]
                                        )
                                    )
                                )
        
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {str(e)}")
        
        completion_time = time.time() - start_time
        
        return AssistantOutput(
            output=actual_output.strip(),
            tools_called=tools_called,
            context=context,
            execution_time=completion_time
        )
