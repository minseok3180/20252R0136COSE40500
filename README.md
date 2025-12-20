# AI 에이전트 with MCP 통합

LangGraph와 MCP(Model Context Protocol)를 활용한 질문-답변 AI 에이전트 시스템입니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [설치 방법](#설치-방법)
- [설정 방법](#설정-방법)
- [사용 방법](#사용-방법)
- [MCP 통합](#mcp-통합)
- [Docker 사용](#docker-사용)
- [기술 스택](#기술-스택)

## ✨ 주요 기능

- **LangGraph 기반 워크플로우**: 질문-답변 처리를 위한 그래프 기반 워크플로우
- **MCP 통합**: Model Context Protocol을 통한 도구 통합 및 답변 포맷팅
- **배치 처리**: JSON 파일을 통한 여러 질문 일괄 처리
- **유연한 설정**: config.json을 통한 LLM 및 MCP 설정 관리

## 📁 프로젝트 구조

```
.
├── main.py                 # 메인 실행 파일
├── config.json             # LLM 및 MCP 설정 파일
├── questions.json          # 입력 질문 파일
├── answers.json           # 출력 결과 파일 (자동 생성)
├── requirements.txt       # Python 패키지 의존성
├── Dockerfile             # Docker 이미지 빌드 파일
├── README.md              # 프로젝트 문서
└── src/
    ├── agent.py           # LangGraph 에이전트 구현
    └── server.py          # MCP 서버 구현
```

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd 20252R0136COSE40500
```

### 2. 가상환경 생성 및 활성화

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

## ⚙️ 설정 방법

### config.json 설정

`config.json` 파일을 열어 다음 정보를 설정합니다:

```json
{
    "model_name": "gpt-4o-mini",
    "openai_api_key": "your-api-key-here",
    "openai_api_base": "https://api.openai.com/v1",
    "use_mcp": true
}
```

**설정 항목 설명:**
- `model_name`: 사용할 OpenAI 모델명 (예: "gpt-4o-mini", "gpt-4")
- `openai_api_key`: OpenAI API 키
- `openai_api_base`: OpenAI API 엔드포인트 URL
- `use_mcp`: MCP 도구 사용 여부 (true/false)

### questions.json 설정

처리할 질문들을 `questions.json` 파일에 작성합니다:

```json
[
    {
        "id": "1",
        "question": "파이썬에서 리스트와 튜플의 차이점은 무엇인가요?"
    },
    {
        "id": "2",
        "question": "머신러닝에서 과적합을 방지하는 방법은 무엇인가요?"
    }
]
```

## 📖 사용 방법

### 기본 실행

```bash
python main.py
```

프로그램이 실행되면:
1. `config.json`에서 설정을 로드합니다
2. `questions.json`에서 질문들을 읽어옵니다
3. 각 질문에 대해 AI 에이전트를 실행합니다
4. 결과를 `answers.json`에 저장합니다

### 실행 결과

`answers.json` 파일에 다음과 같은 형식으로 결과가 저장됩니다:

```json
[
    {
        "id": "1",
        "question": "파이썬에서 리스트와 튜플의 차이점은 무엇인가요?",
        "answer": "### 분석 결과\n\n답변 내용...\n\n---\n*vLLM-MCP 서버에 의해 처리됨*"
    }
]
```

## 🔌 MCP 통합

### MCP란?

MCP(Model Context Protocol)는 AI 모델과 외부 도구/서비스를 연결하는 표준 프로토콜입니다. 이 프로젝트에서는 MCP를 통해 답변 포맷팅 도구를 제공합니다.

### MCP 워크플로우

```
[시작] → [LLM 노드] → [조건부 분기] → [MCP 포맷팅 노드] → [종료]
                              |
                              └→ [종료] (MCP 비활성화 시)
```

1. **LLM 노드**: 사용자 질문을 LLM에 전달하여 원본 답변 생성
2. **조건부 분기**: `use_mcp` 설정에 따라 다음 단계 결정
3. **MCP 포맷팅 노드**: MCP 서버의 `format_answer` 도구로 답변 포맷팅
4. **종료**: 최종 답변 반환

### MCP 서버 도구

현재 제공되는 MCP 도구:
- `format_answer(text: str)`: 답변을 마크다운 형식으로 포맷팅

### MCP 비활성화

MCP 기능을 사용하지 않으려면 `config.json`에서 `"use_mcp": false`로 설정하세요.

## 🐳 Docker 사용

### Docker 이미지 빌드

```bash
docker build -t ai-agent-mcp .
```

### Docker 컨테이너 실행

```bash
docker run -v $(pwd)/config.json:/app/config.json \
           -v $(pwd)/questions.json:/app/questions.json \
           -v $(pwd)/answers.json:/app/answers.json \
           ai-agent-mcp
```

**Windows PowerShell:**
```powershell
docker run -v ${PWD}/config.json:/app/config.json `
           -v ${PWD}/questions.json:/app/questions.json `
           -v ${PWD}/answers.json:/app/answers.json `
           ai-agent-mcp
```

## 🛠 기술 스택

- **Python 3.11+**: 프로그래밍 언어
- **LangChain**: LLM 애플리케이션 프레임워크
- **LangGraph**: 그래프 기반 워크플로우 오케스트레이션
- **MCP (Model Context Protocol)**: AI 도구 통합 프로토콜
- **FastMCP**: MCP 서버 구현 프레임워크
- **OpenAI API**: LLM 서비스

## 📝 주요 파일 설명

### main.py
- 메인 실행 파일
- JSON 파일 로드/저장
- 질문 배치 처리
- 결과 저장

### src/agent.py
- LangGraph 기반 AI 에이전트 구현
- MCP 통합 로직
- 워크플로우 그래프 구성

### src/server.py
- MCP 서버 구현
- `format_answer` 도구 제공
- FastMCP를 통한 서버 실행

## 🔧 문제 해결

### MCP 모듈을 찾을 수 없음

```
Warning: MCP 서버 모듈을 import할 수 없습니다. MCP 기능이 비활성화됩니다.
```

**해결 방법:**
- `requirements.txt`의 패키지가 모두 설치되었는지 확인
- 가상환경이 활성화되어 있는지 확인
- `pip install -r requirements.txt` 재실행

### API 키 오류

OpenAI API 키가 유효하지 않은 경우 오류가 발생합니다. `config.json`의 `openai_api_key`를 확인하세요.

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

