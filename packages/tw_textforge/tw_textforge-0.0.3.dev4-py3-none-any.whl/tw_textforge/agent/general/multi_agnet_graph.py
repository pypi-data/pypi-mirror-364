from tw_textforge.agent.ai_model import AIModel
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from IPython.display import display, Image
from tw_textforge.prompt.general.general_prompt import multi_supervisor_prompt, multi_generator_agent_prompt, multi_extractor_agent_prompt
class GeneralMultiAgentGraph:
    """
    基於 LangGraph 的通用流程圖，使用模型的 tool_calling 功能實現多個角色的協作
    角色包括：
    - supervisor: 監督者，負責監督生成器和提取器的行為，確保它們按照預期工作
    - generator: 生成器，作為監督者的工具；回答問題，不限制回答的格式，避免模型性能下降
    - extractor: 提取器，作為監督者的工具；提取回答內容最重要的資訊，避免開場白或是無關內容影響資料品質
    """
    supervisor_prompt = multi_supervisor_prompt
    generator_agent_prompt = multi_generator_agent_prompt
    extractor_agent_prompt = multi_extractor_agent_prompt
    def __init__(self, supervisor_llm=None, generator_llm=None, generator_llm_tools=[], extractor_llm=None):
        if prompt is None:
            prompt = self.PROMPT 
        self.generator_agent = create_react_agent(
            model=generator_llm,
            tools=generator_llm_tools,
            prompt=self.generator_agent_prompt,
            name="generator_agent",
        )
        self.extractor_agent = create_react_agent(
            model=extractor_llm,
            tools=[],
            prompt=self.extractor_agent_prompt,
            name="extractor_agent",
        )
        
        self.supervisor = create_supervisor(
            model=supervisor_llm,
            agents=[self.generator_agent, self.extractor_agent],
            prompt=self.supervisor_prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()
        self.graph = self.supervisor
    
    def show_graph(self):
        """
        顯示流程圖
        """
        display(Image(self.graph.get_graph().draw_mermaid_png()))