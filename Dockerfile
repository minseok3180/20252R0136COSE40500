# Python 3.11 Slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 및 설정 파일 복사
COPY src/ ./src/
COPY main.py .
COPY questions.json .
COPY config.json .

# 환경 변수 설정 (필요시)
# ENV OPENAI_API_KEY=your_key_here

# 실행 명령
CMD ["python", "main.py"]
