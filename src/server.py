from mcp.server.fastmcp import FastMCP

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("vLLM-MCP-Helper")

@mcp.tool()
def format_answer(text: str) -> str:
    """
    답변을 더 읽기 좋은 형식으로 변환합니다.
    """
    return f"### 분석 결과\n\n{text}\n\n---\n*vLLM-MCP 서버에 의해 처리됨*"

if __name__ == "__main__":
    mcp.run()
