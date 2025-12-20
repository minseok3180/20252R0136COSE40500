"""
MCP (Model Context Protocol) 서버 구현

MCP는 AI 모델과 외부 도구/서비스를 연결하는 표준 프로토콜입니다.
이 모듈은 FastMCP를 사용하여 MCP 서버를 구현하며,
AI 에이전트가 사용할 수 있는 도구(tools)를 제공합니다.

주요 기능:
- FastMCP를 통한 MCP 서버 생성 및 실행
- AI 에이전트가 호출할 수 있는 도구 정의
- 질문-답변 처리 결과 포맷팅
"""

from mcp.server.fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
# FastMCP는 MCP 프로토콜을 간편하게 구현할 수 있게 해주는 프레임워크입니다.
# 서버 이름은 클라이언트가 이 서버를 식별하는 데 사용됩니다.
mcp = FastMCP("vLLM-MCP-Helper")

@mcp.tool()
def format_answer(text: str) -> str:
    """
    MCP 도구(Tool): 답변 포맷팅
    
    AI 에이전트가 생성한 답변을 더 읽기 좋은 형식으로 변환하는 도구입니다.
    이 함수는 @mcp.tool() 데코레이터로 등록되어 MCP 클라이언트가
    호출할 수 있는 도구로 노출됩니다.
    
    Args:
        text (str): 포맷팅할 원본 텍스트 (AI 에이전트의 답변)
    
    Returns:
        str: 마크다운 형식으로 포맷팅된 답변 텍스트
    
    MCP 동작 방식:
        1. AI 에이전트가 이 도구를 호출 요청
        2. MCP 서버가 요청을 받아 이 함수 실행
        3. 포맷팅된 결과를 AI 에이전트에 반환
        4. AI 에이전트가 최종 답변에 통합
    """
    return f"### 분석 결과\n\n{text}\n\n---\n*vLLM-MCP 서버에 의해 처리됨*"

if __name__ == "__main__":
    # MCP 서버 실행
    # 이 서버는 stdio(표준 입출력)를 통해 MCP 클라이언트와 통신합니다.
    # 클라이언트는 JSON-RPC 2.0 프로토콜을 통해 도구를 호출할 수 있습니다.
    mcp.run()
