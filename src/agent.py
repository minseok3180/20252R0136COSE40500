"""
LangGraph 기반 AI 에이전트 구현

이 모듈은 LangGraph를 사용하여 질문-답변 워크플로우를 구현합니다.
MCP(Model Context Protocol)와의 통합을 위해 설계되었으며,
MCP 서버(src/server.py)에서 제공하는 도구를 활용할 수 있습니다.

MCP 통합 구조:
- 이 에이전트는 MCP 클라이언트 역할을 할 수 있습니다
- MCP 서버(src/server.py)의 도구들을 호출하여 답변을 보강할 수 있습니다
- LangGraph의 노드에서 MCP 도구를 호출하여 외부 기능을 활용합니다
"""

import json
import os
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# 에이전트 상태 정의
# TypedDict를 사용하여 워크플로우 전체에서 공유되는 상태를 정의합니다.
# MCP 통합 시 이 상태에 MCP 도구 호출 결과를 추가할 수 있습니다.
class AgentState(TypedDict):
    question: str      # 사용자 질문
    answer: str        # 생성된 답변
    config: dict       # LLM 설정 (API 키, 모델명 등)

def get_llm(config: dict):
    """
    LangChain ChatOpenAI 인스턴스 생성
    
    config.json에서 로드한 설정을 사용하여 LLM을 초기화합니다.
    MCP 서버와 통합 시, 이 LLM이 MCP 도구를 호출하도록 설정할 수 있습니다.
    
    Args:
        config (dict): LLM 설정 딕셔너리
            - model_name: 사용할 모델명
            - openai_api_key: OpenAI API 키
            - openai_api_base: API 엔드포인트 URL
    
    Returns:
        ChatOpenAI: 초기화된 LangChain LLM 인스턴스
    """
    return ChatOpenAI(
        model=config.get("model_name", "gpt-4o-mini"),
        openai_api_key=config.get("openai_api_key"),
        openai_api_base=config.get("openai_api_base"),
        temperature=0.7
    )

def call_model(state: AgentState):
    """
    LangGraph 노드: LLM 호출
    
    에이전트 상태의 질문을 LLM에 전달하여 답변을 생성합니다.
    향후 MCP 통합 시, 이 함수에서 MCP 서버의 도구를 호출하여
    답변을 보강하거나 포맷팅할 수 있습니다.
    
    MCP 통합 예시:
        # MCP 서버의 format_answer 도구 호출
        formatted = mcp_client.call_tool("format_answer", {"text": response.content})
        return {"answer": formatted}
    
    Args:
        state (AgentState): 현재 에이전트 상태
    
    Returns:
        dict: 업데이트된 상태 (answer 필드 포함)
    """
    llm = get_llm(state["config"])
    response = llm.invoke(state["question"])
    return {"answer": response.content}

def create_agent_graph():
    """
    LangGraph 워크플로우 생성
    
    질문-답변 처리를 위한 그래프를 구성합니다.
    현재는 단순한 LLM 호출 구조이지만, MCP 통합 시:
    - MCP 도구 호출 노드 추가 가능
    - 조건부 분기로 MCP 도구 사용 여부 결정 가능
    - 여러 MCP 도구를 순차적으로 호출하는 파이프라인 구성 가능
    
    그래프 구조:
        [시작] -> [LLM 노드] -> [종료]
    
    향후 MCP 통합 구조 예시:
        [시작] -> [LLM 노드] -> [MCP 포맷팅 노드] -> [종료]
    
    Returns:
        CompiledGraph: 컴파일된 LangGraph 인스턴스
    """
    # 그래프 빌더 초기화
    # AgentState를 상태 타입으로 사용하는 워크플로우 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    # "llm" 노드에 call_model 함수를 연결
    # MCP 통합 시 여기에 MCP 도구 호출 노드를 추가할 수 있습니다
    workflow.add_node("llm", call_model)
    
    # 엣지 설정
    # 워크플로우의 진입점을 "llm" 노드로 설정
    workflow.set_entry_point("llm")
    # "llm" 노드에서 종료로 연결
    workflow.add_edge("llm", END)
    
    # 그래프 컴파일하여 실행 가능한 형태로 반환
    return workflow.compile()

def run_agent(question: str, config: dict) -> str:
    """
    에이전트 실행 함수
    
    질문을 받아 LangGraph 워크플로우를 실행하고 답변을 반환합니다.
    main.py에서 호출되며, MCP 서버와 통합된 환경에서도 사용 가능합니다.
    
    MCP 통합 시나리오:
        1. 이 함수가 MCP 클라이언트로 동작
        2. MCP 서버(src/server.py)의 도구들을 호출
        3. 도구 결과를 활용하여 최종 답변 생성
    
    Args:
        question (str): 처리할 사용자 질문
        config (dict): LLM 및 MCP 설정
    
    Returns:
        str: 생성된 답변 텍스트
    """
    app = create_agent_graph()
    result = app.invoke({"question": question, "config": config})
    return result["answer"]
