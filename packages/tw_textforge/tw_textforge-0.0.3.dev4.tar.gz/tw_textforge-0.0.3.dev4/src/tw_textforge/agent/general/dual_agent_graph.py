from tw_textforge.agent.ai_model import AIModel
from IPython.display import display, Image
from tw_textforge.prompt.general.general_prompt import dual_generator_agent_prompt, dual_extractor_agent_prompt
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Literal
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
class GeneralDualAgentGraph:
    """
    基於 LangGraph 的通用流程圖，使用模型的 tool_calling 功能實現多個角色的協作
    角色包括：
    - generator: 生成器，回答問題，不限制回答的格式，避免模型性能下降
    - extractor: 提取器，提取回答內容的重要資訊，避免開場白或是無關內容影響資料品質
    """
    generator_agent_prompt = dual_generator_agent_prompt
    extractor_agent_prompt = dual_extractor_agent_prompt
    def __init__(self, generator_llm=None, generator_llm_tools=[], extractor_llm=None):
        if generator_llm is None:
            generator_llm = AIModel().llm
        if extractor_llm is None:
            extractor_llm = AIModel().llm
        tool_node = ToolNode(generator_llm_tools)
        generator_llm_with_tools = generator_llm.bind_tools(generator_llm_tools)
        
        def generator_agent(state: MessagesState):
            state["messages"].insert(0, SystemMessage(content=self.generator_agent_prompt))
            response = generator_llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}
        
        def extractor_agent(state: MessagesState):
            wrapped = HumanMessage(content=f"{self.extractor_agent_prompt}\n{state["messages"][-1].content}")
            response = extractor_llm.invoke(state["messages"] + [wrapped])
            return {"messages": [response]}
        
        def should_continue(state: MessagesState) -> Literal["tools", "extractor_agent"]:
            messages = state["messages"]
            last_message = messages[-1]
            for tool in last_message.tool_calls:
                return "tools"
            return "extractor_agent"
        
        builder = StateGraph(MessagesState)
        builder.add_node(generator_agent)
        builder.add_node("tools", tool_node)
        builder.add_node(extractor_agent)
        
        builder.add_edge(START, "generator_agent")
        builder.add_conditional_edges(
            "generator_agent",
            should_continue,
        )
        builder.add_edge("tools", "generator_agent")
        builder.add_edge("generator_agent", "extractor_agent")
        builder.add_edge("extractor_agent", END)
        self.graph = builder.compile()
    
    def show_graph(self):
        """
        顯示流程圖
        """
        display(Image(self.graph.get_graph().draw_mermaid_png()))