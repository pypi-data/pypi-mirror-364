from collections.abc import Callable
from langchain_core.language_models.chat_models import BaseChatModel
from inspect import getmembers, isfunction, signature
from langchain.prompts import PromptTemplate
import logging
import warnings
from typing import get_type_hints, get_args

__version__ = "0.2.0"

_tools = dict() 

def clear_all_functions():
    global _tools
    _tools = dict()

log = logging.getLogger("agentic_tools")

class Agent:
    def __init__(self, llm_chat_model: BaseChatModel):
        self.llm = llm_chat_model

    def __build_promt(self, question:str) -> PromptTemplate:
        global _tools
        all_tools = "".join([f"- USE_TOOL:{t["use"]}\n" for _, t in _tools.items()])
        all_sigs = "".join([f"{t["sig"]}\n" for _, t in _tools.items()])
        #- USE_TOOL:func_name:arg1,arg2
        template = f"""
Here is a list of avilabel functions: 

{all_sigs}
    
Based on the user's question, respond with one of the following and replace <arg> with the apropriate value:

{all_tools}

If the question is not about any of these, answer normally.

Question: {question}
"""
        log.debug(template)
        return PromptTemplate(template=template, input_variables=["question"])

    def query(self, question:str, got_error:bool=False) -> str: 
        prompt = self.__build_promt(question)
        chain = prompt | self.llm

        llm_response = chain.invoke({"question": question})
        response_text = llm_response.content.strip()
        log.debug(response_text)
        if "USE_TOOL:" in response_text: 
            response_text = "USE_TOOL:" + response_text.split("USE_TOOL:")[1]
        if response_text.startswith("USE_TOOL:"):
            tool_name = response_text.split(":")[1]
            args = response_text[:-1].split(":")[2].split(",")
            func = _tools[tool_name]["func"]
            args = [arg.strip() for arg in args] 
            args = [arg for arg in args if arg != ""] 
            hints = get_type_hints(func)
            if len(hints) > 0:
                if "return" in hints: 
                    hints.pop("return")
                if len(hints) == len(args):
                    for i, t in enumerate(hints.values()):
                        if get_args(t) != ():
                            args[i] = get_args(t)[0](args[i]) 
                        else: 
                            args[i] = t(args[i]) 
                        

            log.debug(f"calling {tool_name} with args {args}")
            result = ""
            if tool_name in _tools:
                try:
                    result = func(*args)
                except Exception as e: 
                    log.warning(f"Got error when calling tool")
                    if not got_error:
                        new_question = f"""
{question}


But you got error: ```{e}```
So re-try the tool response. 
Might be worth trying a new argument value if the function takes a argument. 
GIVE ONLY THE TOOL RESPONSE.
"""
                        result = self.query(question=new_question, got_error=True)
                    else: 
                        print(f"error: {tool_name}(*{args})")
                        result = ""
            else:
                result = f"Unknown tool: {tool_name}"
            return result 
        else:
            return response_text



def ai_tool(func:Callable):
    global _tools
    if not isfunction(func): 
        raise ValueError(f"agentic_tools.ai_tool is for functions, {func.__name__} is not a function")

    _tools[func.__name__] = {
        "func":func,
        "use":f"{func.__name__}:{''.join([f'<{arg}>,' for arg in func.__code__.co_varnames[:func.__code__.co_argcount]])};",
        "sig":f"{func.__name__}{str(signature(func))} docstring:{func.__doc__};",
    }    
    def wrapper(*args, **kw):
        return func(*args, **kw) 
    return wrapper