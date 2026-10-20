import os
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq
from termcolor import colored

# 1. 환경 변수 불러오기 (.env)
load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-2.0-flash"

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_gemini(messages):
    """Groq 한도 소진 시 Gemini(OpenAI 호환 엔드포인트)로 대체"""
    from openai import OpenAI

    gemini = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    res = gemini.chat.completions.create(model=GEMINI_MODEL, messages=messages)
    return res.choices[0].message.content


def ask(messages):
    """Groq로 먼저 요청하고, 실패하면 Gemini로 전환"""
    try:
        res = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.5,
            max_completion_tokens=800,
            reasoning_effort="low",
        )
        return res.choices[0].message.content
    except Exception as e:
        if not os.getenv("GEMINI_API_KEY"):
            raise
        print(colored(f"[Groq 오류 -> Gemini로 전환] {e}", "yellow"))
        return ask_gemini(messages)


def build_system_prompt(job, level, count):
    return (
        f"너는 '{job}' 직무의 면접관이야. 난이도는 '{level}'.\n"
        "규칙:\n"
        "1. 한 번에 질문 하나만 한다.\n"
        "2. 지원자가 답하면 한두 문장으로 짧게 피드백(좋은 점/보완점)을 주고, 다음 질문을 한다.\n"
        f"3. 총 {count}개의 질문을 하고, 마지막 답변 후에는 질문 대신 "
        "'종합 평가'(점수 100점 만점, 강점, 개선점)를 준다.\n"
        "4. 한국어로 답하고, 실제 면접처럼 정중하지만 날카롭게 한다."
    )


def save_log(messages, job):
    os.makedirs("logs", exist_ok=True)
    path = f"logs/interview_{datetime.now():%Y%m%d_%H%M%S}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"직무: {job}\n\n")
        for m in messages:
            if m["role"] == "system":
                continue
            who = "나" if m["role"] == "user" else "면접관"
            f.write(f"[{who}] {m['content']}\n\n")
    return path


def choose(prompt, options):
    print(prompt)
    for i, o in enumerate(options, 1):
        print(f"  {i}. {o}")
    while True:
        s = input("번호 선택 : ").strip()
        if s.isdigit() and 1 <= int(s) <= len(options):
            return options[int(s) - 1]
        print("올바른 번호를 입력하세요.")


def main():
    print(colored("=== 면접 연습 챗봇 ===", "cyan"))
    job = input("지원 직무를 입력하세요 (예: 백엔드 개발자) : ").strip() or "개발자"
    level = choose("난이도를 선택하세요", ["쉬움", "보통", "어려움"])
    count = int(choose("질문 개수를 선택하세요", ["3", "5", "7"]))

    system = {"role": "system", "content": build_system_prompt(job, level, count)}
    messages = [system]
    print(colored("\n명령어: /reset 다시 시작, /save 기록 저장, exit 종료\n", "cyan"))

    # 면접관이 먼저 인사하고 첫 질문
    messages.append({"role": "user", "content": "면접을 시작해주세요."})
    answer = ask(messages)
    print(colored(f"면접관 : {answer}\n", "blue"))
    messages.append({"role": "assistant", "content": answer})

    while True:
        q = input("나 : ").strip()
        if not q:
            continue
        if q == "exit":
            print("면접을 종료합니다. 수고하셨습니다!")
            break
        if q == "/reset":
            messages = [system]
            messages.append({"role": "user", "content": "면접을 시작해주세요."})
            answer = ask(messages)
            print(colored(f"면접관 : {answer}\n", "blue"))
            messages.append({"role": "assistant", "content": answer})
            continue
        if q == "/save":
            print(f"저장 완료: {save_log(messages, job)}")
            continue

        messages.append({"role": "user", "content": q})
        try:
            answer = ask(messages)
        except Exception as e:
            print(colored(f"요청 실패: {e}", "red"))
            messages.pop()
            continue
        print(colored(f"\n면접관 : {answer}\n", "blue"))
        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
