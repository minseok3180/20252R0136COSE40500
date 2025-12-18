import json
import os
from src.agent import run_agent

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    # 설정 로드
    config = load_json("config.json")
    if not config:
        print("Error: config.json이 없습니다.")
        return

    # 질문 로드
    questions = load_json("questions.json")
    if not questions:
        print("Error: questions.json에 질문이 없습니다.")
        return

    results = []
    print(f"총 {len(questions)}개의 질문 처리를 시작합니다...")

    for item in questions:
        q_id = item.get("id")
        question = item.get("question")
        
        print(f"[{q_id}] 처리 중: {question[:30]}...")
        
        try:
            # 에이전트 실행
            answer = run_agent(question, config)
            
            results.append({
                "id": q_id,
                "question": question,
                "answer": answer
            })
        except Exception as e:
            print(f"Error 처리 중 {q_id}: {e}")
            results.append({
                "id": q_id,
                "question": question,
                "error": str(e)
            })

    # 결과 저장
    save_json("answers.json", results)
    print("모든 질문 처리가 완료되었습니다. 결과가 answers.json에 저장되었습니다.")

if __name__ == "__main__":
    main()
