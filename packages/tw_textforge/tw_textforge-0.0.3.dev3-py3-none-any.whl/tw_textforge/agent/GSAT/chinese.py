from tw_textforge.agent.general.single_agent_graph import GeneralSingleAgentGraph
from tw_textforge.prompt.GSAT.chinese import gast_chinese_question_analysis_generator_prompt

class GSATChineseGraph_QuestionAnalysis(GeneralSingleAgentGraph):
    """
    產生學測國綜試題的題目分析
    """
    prompt = gast_chinese_question_analysis_generator_prompt