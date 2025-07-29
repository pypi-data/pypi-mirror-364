from langgraph.prebuilt import create_react_agent
from IPython.display import display, Image
from tw_textforge.prompt.general.general_prompt import single_generator_agent_prompt
class GeneralSingleAgentGraph:
    """
    基於 LangGraph 的通用單代理流程圖
    """
    prompt = single_generator_agent_prompt
    def __init__(self, generator_llm, generator_llm_tools):
        self.graph = create_react_agent(
            model=generator_llm,
            tools=generator_llm_tools,
            prompt=self.prompt,
            name="generator_agent",
        )
    
    def show_graph(self):
        """
        顯示流程圖
        """
        display(Image(self.graph.get_graph().draw_mermaid_png()))