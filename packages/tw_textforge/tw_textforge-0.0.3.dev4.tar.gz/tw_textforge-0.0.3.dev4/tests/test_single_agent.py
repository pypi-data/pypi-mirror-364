import pytest


def test_dataset_upload():
    """測試單 agent 的 Graph 是否正常回傳內容"""
    from langchain_core.messages import HumanMessage, AIMessage
    from tw_textforge.agent.general.single_agent_graph import GeneralSingleAgentGraph
    generalgraph_obj = GeneralSingleAgentGraph()
    try:
        chucks = generalgraph_obj.graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "在軟體工程中，什麼是資料庫?",
                    }
                ]
            },
        )
        if not chucks:
            pytest.fail("Graph 回傳內容為空")
        elif not isinstance(chucks["messages"][0], HumanMessage):
            pytest.fail("Graph 回傳內容的第一個訊息不是 HumanMessage")
            
        elif not isinstance(chucks["messages"][-1], AIMessage):
            pytest.fail("Graph 回傳內容的最後一個訊息不是 AIMessage")
        else:
            print("單 agent Graph invoke 成功:")
            print(chucks)
    except Exception as e:
        pytest.fail(f"Graph invoke 失敗: {e}")
        assert False, f"Graph invoke 失敗: {e}"

if __name__ == "__main__":
    pytest.main([__file__])