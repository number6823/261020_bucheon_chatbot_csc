# 면접 연습 챗봇 (261020_bucheon_chatbot_csc)

Groq API를 활용한 터미널 기반 **면접 연습 챗봇**입니다.
직무와 난이도를 고르면 AI 면접관이 질문하고, 답변마다 피드백을 주며, 마지막에 종합 평가(점수/강점/개선점)를 제공합니다.

## 기능
- 직무 입력, 난이도(쉬움/보통/어려움), 질문 개수(3/5/7) 선택
- 대화 기록을 유지하는 면접 진행
- 답변별 짧은 피드백 + 마지막 종합 평가
- `/reset` 면접 다시 시작, `/save` 대화 기록 저장(`logs/`), `exit` 종료
- Groq 오류(한도 소진 등) 시 Gemini로 자동 전환 (`GEMINI_API_KEY` 설정 시)

## 설치
```bash
git clone https://github.com/number6823/261020_bucheon_chatbot_csc.git
cd 261020_bucheon_chatbot_csc
pip install -r requirements.txt
```

## 환경 변수 설정
`.env.example`을 복사해 `.env`를 만들고 키를 입력합니다.
```bash
copy .env.example .env      # macOS/Linux: cp .env.example .env
```
```
GROQ_API_KEY=발급받은_키
GEMINI_API_KEY=발급받은_키   # 선택
```
> `.env`는 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다.

## 실행
```bash
python main.py
```

## 사용 예시
```
지원 직무를 입력하세요 : 백엔드 개발자
번호 선택 : 2   (난이도 보통)
면접관 : 안녕하세요. 먼저 간단히 자기소개 부탁드립니다.
나 : 저는 ...
```

## 사용 기술
Python, Groq API (`openai/gpt-oss-20b`), python-dotenv, termcolor
