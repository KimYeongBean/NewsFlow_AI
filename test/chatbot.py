# chatbot.py

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def main():
    """
    터미널에서 실행되는 간단한 챗봇 프로그램입니다.
    """
    # 1. .env 파일에서 Azure OpenAI 접속 정보 불러오기
    load_dotenv()

    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        # 필수 정보가 없는 경우 오류 발생
        if not all([endpoint, api_key, deployment_name, api_version]):
            raise ValueError("환경 변수(.env 파일)에 Azure OpenAI 정보가 올바르게 설정되지 않았습니다.")

        # Azure OpenAI 클라이언트 초기화
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
    except Exception as e:
        print(f"오류: 초기화에 실패했습니다. - {e}")
        return # 프로그램 종료

    print("=========================================")
    print("🎉 독립형 챗봇을 시작합니다.")
    print("대화를 종료하려면 '종료' 또는 'exit'를 입력하세요.")
    print("=========================================")

    # 2. 대화 기록을 저장할 리스트 (AI의 역할을 미리 설정)
    messages = [
        {"role": "system", "content": "당신은 사용자의 질문에 친절하고 상세하게 답변하는 AI 어시스턴트입니다."}
    ]

    # 3. 사용자와 계속 대화하기 위한 무한 루프
    while True:
        # 사용자 입력 받기
        user_input = input("나 (User): ")

        # 종료 명령어 확인
        if user_input.lower() in ["종료", "exit", "quit"]:
            print("챗봇을 종료합니다. 이용해주셔서 감사합니다.")
            break

        # 대화 기록에 사용자 메시지 추가
        messages.append({"role": "user", "content": user_input})

        try:
            # Azure OpenAI API에 요청 보내기
            response = client.chat.completions.create(
                model=deployment_name,
                messages=messages
            )

            # AI의 답변 추출
            bot_response = response.choices[0].message.content
            print(f"챗봇 (AI): {bot_response}")

            # 대화 기록에 AI 답변 추가 (대화의 맥락을 기억하게 함)
            messages.append({"role": "assistant", "content": bot_response})

        except Exception as e:
            print(f"오류: API 호출 중 문제가 발생했습니다. - {e}")
            # 문제가 발생한 마지막 사용자 입력을 기록에서 제거
            messages.pop()

if __name__ == "__main__":
    main()
