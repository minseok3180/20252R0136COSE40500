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
import sys
from typing import TypedDict, Annotated, List, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# MCP 서버의 도구를 직접 import하여 사용
# 같은 프로세스 내에서 실행하는 경우 직접 호출이 더 효율적입니다
try:
    from src.server import format_answer as mcp_format_answer
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP 서버 모듈을 import할 수 없습니다. MCP 기능이 비활성화됩니다.")

# 에이전트 상태 정의
# TypedDict를 사용하여 워크플로우 전체에서 공유되는 상태를 정의합니다.
# MCP 통합 시 이 상태에 MCP 도구 호출 결과를 추가할 수 있습니다.
class AgentState(TypedDict):
    question: str          # 사용자 질문
    answer: str            # 생성된 답변
    raw_answer: str        # MCP 포맷팅 전 원본 답변
    config: dict           # LLM 설정 (API 키, 모델명 등)
    use_mcp: bool          # MCP 도구 사용 여부

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
    MCP 통합: 원본 답변을 raw_answer에 저장하여 후속 노드에서 사용합니다.
    
    Args:
        state (AgentState): 현재 에이전트 상태
    
    Returns:
        dict: 업데이트된 상태 (raw_answer 필드 포함)
    """
    llm = get_llm(state["config"])
    response = llm.invoke(state["question"])
    return {"raw_answer": response.content, "answer": response.content}

def call_mcp_format(state: AgentState):
    """
    LangGraph 노드: MCP 포맷팅 도구 호출
    
    MCP 서버의 format_answer 도구를 호출하여 답변을 포맷팅합니다.
    이 노드는 MCP 통합의 핵심으로, MCP 서버에서 제공하는 도구를
    LangGraph 워크플로우에 통합합니다.
    
    MCP 통합 동작:
        1. raw_answer(원본 답변)를 MCP 서버의 format_answer 도구에 전달
        2. MCP 서버가 마크다운 형식으로 포맷팅된 답변 반환
        3. 포맷팅된 답변을 answer 필드에 저장
    
    Args:
        state (AgentState): 현재 에이전트 상태 (raw_answer 포함)
    
    Returns:
        dict: 업데이트된 상태 (포맷팅된 answer 필드 포함)
    """
    if not MCP_AVAILABLE:
        # MCP가 사용 불가능한 경우 원본 답변 그대로 반환
        return {"answer": state.get("raw_answer", state.get("answer", ""))}
    
    raw_answer = state.get("raw_answer", state.get("answer", ""))
    try:
        # MCP 서버의 format_answer 도구 호출
        formatted_answer = mcp_format_answer(raw_answer)
        return {"answer": formatted_answer}
    except Exception as e:
        print(f"MCP 포맷팅 오류: {e}")
        # 오류 발생 시 원본 답변 반환
        return {"answer": raw_answer}

def should_use_mcp(state: AgentState) -> str:
    """
    조건부 라우팅 함수: MCP 사용 여부 결정
    
    config에서 use_mcp 설정을 확인하여 다음 노드를 결정합니다.
    MCP가 활성화되어 있고 사용 가능한 경우 "mcp_format" 노드로,
    그렇지 않은 경우 END로 이동합니다.
    
    Args:
        state (AgentState): 현재 에이전트 상태
    
    Returns:
        str: 다음 노드 이름 ("mcp_format" 또는 END)
    """
    use_mcp = state.get("use_mcp", True) and MCP_AVAILABLE
    return "mcp_format" if use_mcp else END

def create_agent_graph():
    """
    LangGraph 워크플로우 생성 (MCP 통합)
    
    질문-답변 처리를 위한 그래프를 구성하며, MCP 도구를 통합합니다.
    
    그래프 구조 (MCP 통합):
        [시작] -> [LLM 노드] -> [조건부 분기] -> [MCP 포맷팅 노드] -> [종료]
                                      |
                                      └-> [종료] (MCP 비활성화 시)
    
    워크플로우 단계:
        1. LLM 노드: 사용자 질문을 LLM에 전달하여 원본 답변 생성
        2. 조건부 분기: MCP 사용 여부에 따라 다음 노드 결정
        3. MCP 포맷팅 노드: MCP 서버의 format_answer 도구로 답변 포맷팅
        4. 종료: 최종 답변 반환
    
    Returns:
        CompiledGraph: 컴파일된 LangGraph 인스턴스
    """
    # 그래프 빌더 초기화
    # AgentState를 상태 타입으로 사용하는 워크플로우 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    # 1. LLM 노드: 질문을 LLM에 전달하여 답변 생성
    workflow.add_node("llm", call_model)
    
    # 2. MCP 포맷팅 노드: MCP 서버의 도구를 사용하여 답변 포맷팅
    if MCP_AVAILABLE:
        workflow.add_node("mcp_format", call_mcp_format)
    
    # 엣지 설정
    # 워크플로우의 진입점을 "llm" 노드로 설정
    workflow.set_entry_point("llm")
    
    # 조건부 엣지: MCP 사용 여부에 따라 분기
    if MCP_AVAILABLE:
        workflow.add_conditional_edges(
            "llm",
            should_use_mcp,
            {
                "mcp_format": "mcp_format",
                END: END
            }
        )
        # MCP 포맷팅 후 종료
        workflow.add_edge("mcp_format", END)
    else:
        # MCP가 사용 불가능한 경우 LLM 노드에서 직접 종료
        workflow.add_edge("llm", END)
    
    # 그래프 컴파일하여 실행 가능한 형태로 반환
    return workflow.compile()

def run_agent(question: str, config: dict) -> str:
    """
    에이전트 실행 함수 (MCP 통합)
    
    질문을 받아 LangGraph 워크플로우를 실행하고 답변을 반환합니다.
    MCP 서버와 통합되어 있어, LLM이 생성한 답변을 MCP 도구로 포맷팅합니다.
    
    MCP 통합 동작 흐름:
        1. LangGraph 워크플로우 시작
        2. LLM 노드에서 질문 처리 및 원본 답변 생성
        3. 조건부 분기: MCP 사용 여부 확인
        4. MCP 포맷팅 노드에서 format_answer 도구 호출
        5. 포맷팅된 최종 답변 반환
    
    Args:
        question (str): 처리할 사용자 질문
        config (dict): LLM 및 MCP 설정
            - use_mcp (bool, optional): MCP 사용 여부 (기본값: True)
            - 기타 LLM 설정 (model_name, openai_api_key 등)
    
    Returns:
        str: 생성된 답변 텍스트 (MCP 포맷팅 적용됨)
    """
    app = create_agent_graph()
    
    # MCP 사용 여부 설정 (기본값: True)
    use_mcp = config.get("use_mcp", True) if isinstance(config, dict) else True
    
    # 초기 상태 설정
    initial_state = {
        "question": question,
        "config": config,
        "use_mcp": use_mcp and MCP_AVAILABLE,
        "answer": "",
        "raw_answer": ""
    }
    
    # 워크플로우 실행
    result = app.invoke(initial_state)
    
    # 최종 답변 반환
    return result.get("answer", "")
