from typing import Any, Dict, Optional
from .provider import BaseProvider
from .session import Session
from .memory import Memory
from .vector_memory import VectorMemory
import asyncio
from .browser_cookie import get_cookies_from_url

class Agent:
    def __init__(self, provider: BaseProvider, session: Optional[Session] = None, memory: Optional[Memory] = None, context_window: int = 10, vector_memory: Optional[VectorMemory] = None, url_for_cookies: str = None, cookie_wait_time: int = 60, browser: str = 'chrome', headless: bool = False):
        if session is None and url_for_cookies:
            cookies = get_cookies_from_url(url_for_cookies, wait_time=cookie_wait_time, browser=browser, headless=headless)
            session = Session(cookies)
        self.provider = provider
        self.session = session or Session()
        self.tools = {}
        self.memory = memory or Memory()
        self.context_window = context_window
        self.vector_memory = vector_memory or VectorMemory()
        self.integrations = {}

    def register_tool(self, tool):
        self.tools[tool.name] = tool

    def call_tool(self, name, *args, **kwargs):
        if name not in self.tools:
            self.memory.add_message("system", f"Tool '{name}' not registered.")
            raise ValueError(f"Tool '{name}' not registered.")
        try:
            result = self.tools[name].run(*args, **kwargs)
            self.memory.add_message("tool", f"{name}({args}, {kwargs}) -> {result}")
            return result
        except Exception as e:
            self.memory.add_message("system", f"Tool '{name}' error: {e}")
            return {"error": f"Tool '{name}' error: {e}"}

    def register_integration(self, name: str, func):
        self.integrations[name] = func

    def call_integration(self, name: str, *args, **kwargs):
        if name not in self.integrations:
            self.memory.add_message("system", f"Integration '{name}' not registered.")
            raise ValueError(f"Integration '{name}' not registered.")
        try:
            result = self.integrations[name](*args, **kwargs)
            self.memory.add_message("integration", f"{name}({args}, {kwargs}) -> {result}")
            return result
        except Exception as e:
            self.memory.add_message("system", f"Integration '{name}' error: {e}")
            return {"error": f"Integration '{name}' error: {e}"}

    def add_to_vector_memory(self, text: str, meta: any = None):
        self.vector_memory.add(text, meta)

    def retrieve_relevant_memory(self, query: str, top_k: int = 3) -> list:
        return self.vector_memory.search(query, top_k=top_k)

    def run(self, prompt: str, use_semantic_context: bool = False, **kwargs) -> Any:
        self.memory.add_message("user", prompt)
        if use_semantic_context:
            # Use semantic retrieval for context
            context = [
                {"role": "retrieved", "content": t}
                for t, _, _ in self.retrieve_relevant_memory(prompt, top_k=self.context_window)
            ]
        else:
            context = self.memory.get_messages(self.context_window)
        try:
            result = self.provider.generate(prompt, session=self.session, context=context, **kwargs)
        except Exception as e:
            self.memory.add_message("system", f"LLM error: {e}")
            return {"error": f"LLM error: {e}"}
        if isinstance(result, str):
            self.memory.add_message("assistant", result)
            self.add_to_vector_memory(result)
        return result

    def run_with_tools(self, prompt: str, tool_pattern: str = "TOOL:") -> Any:
        """
        Run the agent with LLM and tool support. If the LLM output contains a tool call pattern,
        parse and invoke the tool, otherwise return the LLM output.
        Example tool call format: 'TOOL: add {"a": 2, "b": 3}'
        """
        llm_output = self.run(prompt)
        if isinstance(llm_output, str) and tool_pattern in llm_output:
            # Example: 'TOOL: add {"a": 2, "b": 3}'
            try:
                import re, json
                match = re.search(rf"{tool_pattern}\s*(\w+)\s*(\{{.*\}})", llm_output)
                if match:
                    tool_name = match.group(1)
                    arg_str = match.group(2)
                    args = json.loads(arg_str)
                    return self.call_tool(tool_name, **args)
            except Exception as e:
                self.memory.add_message("system", f"Tool call parse error: {e}")
                return {"error": f"Failed to parse tool call: {e}", "llm_output": llm_output}
        return llm_output

    def run_agentic_loop(self, initial_prompt: str, tool_pattern: str = "TOOL:", max_steps: int = 5) -> Any:
        """
        Multi-step agentic loop: alternate between LLM and tool calls until a final answer is produced
        or a step limit is reached. Tool results are injected into the next LLM prompt.
        """
        prompt = initial_prompt
        for step in range(max_steps):
            llm_output = self.run(prompt)
            if isinstance(llm_output, str) and tool_pattern in llm_output:
                try:
                    import re, json
                    match = re.search(rf"{tool_pattern}\s*(\w+)\s*(\{{.*\}})", llm_output)
                    if match:
                        tool_name = match.group(1)
                        arg_str = match.group(2)
                        args = json.loads(arg_str)
                        tool_result = self.call_tool(tool_name, **args)
                        # Inject tool result into next prompt
                        prompt = f"Tool '{tool_name}' result: {tool_result}\nContinue."
                        continue
                except Exception as e:
                    self.memory.add_message("system", f"Tool call parse error: {e}")
                    return {"error": f"Failed to parse tool call: {e}", "llm_output": llm_output}
            # If no tool call, return the LLM output as the final answer
            return llm_output
        self.memory.add_message("system", "Step limit reached.")
        return {"error": "Step limit reached", "last_output": llm_output}

    def stream_run(self, prompt: str, **kwargs):
        """
        Stream LLM/tool responses if the provider supports it. Yields tokens/chunks.
        """
        self.memory.add_message("user", prompt)
        context = self.memory.get_messages(self.context_window)
        if hasattr(self.provider, "stream_generate"):
            try:
                for chunk in self.provider.stream_generate(prompt, session=self.session, context=context, **kwargs):
                    yield chunk
            except Exception as e:
                self.memory.add_message("system", f"LLM streaming error: {e}")
                yield {"error": f"LLM streaming error: {e}"}
        else:
            # Fallback: yield the full response
            result = self.run(prompt, **kwargs)
            yield result

    async def async_run(self, prompt: str, use_semantic_context: bool = False, **kwargs) -> Any:
        self.memory.add_message("user", prompt)
        if use_semantic_context:
            context = [
                {"role": "retrieved", "content": t}
                for t, _, _ in self.retrieve_relevant_memory(prompt, top_k=self.context_window)
            ]
        else:
            context = self.memory.get_messages(self.context_window)
        if hasattr(self.provider, "async_generate"):
            try:
                result = await self.provider.async_generate(prompt, session=self.session, context=context, **kwargs)
            except Exception as e:
                self.memory.add_message("system", f"LLM error: {e}")
                return {"error": f"LLM error: {e}"}
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.provider.generate, prompt, self.session, context)
        if isinstance(result, str):
            self.memory.add_message("assistant", result)
            self.add_to_vector_memory(result)
        return result

    async def async_stream_run(self, prompt: str, **kwargs):
        self.memory.add_message("user", prompt)
        context = self.memory.get_messages(self.context_window)
        if hasattr(self.provider, "async_stream_generate"):
            try:
                async for chunk in self.provider.async_stream_generate(prompt, session=self.session, context=context, **kwargs):
                    yield chunk
            except Exception as e:
                self.memory.add_message("system", f"LLM streaming error: {e}")
                yield {"error": f"LLM streaming error: {e}"}
        elif hasattr(self.provider, "stream_generate"):
            for chunk in self.provider.stream_generate(prompt, session=self.session, context=context, **kwargs):
                yield chunk
        else:
            result = await self.async_run(prompt, **kwargs)
            yield result 