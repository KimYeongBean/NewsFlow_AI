from openai import AzureOpenAI

# -----------------------------
# 1. Azure OpenAI 정보 직접 입력
# -----------------------------
endpoint = "https://newscheck2.openai.azure.com/"
deployment = "gpt-5-nano"
subscription_key = "Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53"

# -----------------------------
# 2. Azure OpenAI 클라이언트 초기화
# -----------------------------
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

# -----------------------------
# 3. 사용자 입력 예시
# -----------------------------
user_selected_sources = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]
news_to_check = """
[검증할 뉴스 기사 내용]
여기에 사용자가 확인하고 싶은 뉴스 본문을 넣습니다.
"""

# -----------------------------
# 4. GPT 프롬프트 구성
# -----------------------------
prompt_text = f"""
사용자가 선택한 5개 언론사: {', '.join(user_selected_sources)}
다음 뉴스 기사를 3줄로 요약하고, 선택한 5개 언론사 기준으로 비교해주세요. 
- 비교 방법: 동일 이슈를 다룬 다른 핵심 언론사 기사와 핵심 주장 일치도 확인
- 신뢰도 점수 계산: 100 - ((정정 보도 건수 + 가짜뉴스 건수) * 1.25)
- 점수 등급:
    - 높음: >= 70
    - 보통: >= 40
    - 낮음: < 40
출력 형식:
1) 3줄 요약
2) 다른 언론사와 비교 결과
3) 점수
4) 신뢰도 등급
"""

# -----------------------------
# 5. 메시지 구성
# -----------------------------
messages = [
    {"role": "user", "content": news_to_check},
    {"role": "assistant", "content": prompt_text}
]

# -----------------------------
# 6. GPT 호출
# -----------------------------
try:
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_completion_tokens=2048,
        stop=None
    )

    result_text = completion.choices[0].message.content
    print("===== GPT 결과 =====")
    print(result_text)

except Exception as e:
    print("오류 발생:", e)
