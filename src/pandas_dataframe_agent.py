"""Agent for working with pandas objects."""
from typing import Any, List, Optional, Sequence

from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits.pandas.prompt import PREFIX, SUFFIX
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.tools.python.tool import PythonAstREPLTool
from langchain.tools.base import BaseTool


def create_pandas_dataframe_agent_with_tools(
    tools: Sequence[BaseTool],
    llm: BaseLLM,
    df: Any,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = PREFIX,
    suffix: str = SUFFIX,
    input_variables: Optional[List[str]] = None,
    verbose: bool = False,
    return_intermediate_steps: bool = False,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    **kwargs: Any,
) -> AgentExecutor:
    """Construct a pandas agent from an LLM and dataframe."""
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected pandas object, got {type(df)}")
    if input_variables is None:
        input_variables = ["df", "input", "agent_scratchpad"]
    all_tools = [PythonAstREPLTool(locals={"df": df}), *tools]
    prompt = ZeroShotAgent.create_prompt(
        all_tools, prefix=prefix, suffix=suffix, input_variables=input_variables
    )
    partial_prompt = prompt.partial(df=str(df.head()))
    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in all_tools]
    agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=all_tools,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
    )
