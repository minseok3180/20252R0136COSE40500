import json
import os
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# 상태 정의
class AgentState(TypedDict):
    question: str
    answer: str
    config: dict

def get_llm(config: dict):
    return ChatOpenAI(
        model=config.get("model_name", "gpt-4o-mini"),
        openai_api_key=config.get("openai_api_key"),
        openai_api_base=config.get("openai_api_base"),
        temperature=0.7
    )

def call_model(state: AgentState):
    llm = get_llm(state["config"])
    response = llm.invoke(state["question"])
    return {"answer": response.content}

def create_agent_graph():
    # 그래프 빌더 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("llm", call_model)
    
    # 엣지 설정
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    
    return workflow.compile()

def run_agent(question: str, config: dict) -> str:
    app = create_agent_graph()
    result = app.invoke({"question": question, "config": config})
    return result["answer"]
