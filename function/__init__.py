# __init__.py

import logging
import requests  # HTTP 요청을 보내기 위한 라이브러리
import os        # 환경 변수를 읽기 위한 라이브러리
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    """
    이 함수는 정해진 시간마다 실행되어 백엔드 API를 호출합니다.
    """
    logging.info('Python timer trigger function executed.')

    # 1. Azure Portal에 설정된 환경 변수에서 백엔드 URL을 안전하게 가져옵니다.
    backend_url = os.environ.get('BACKEND_API_URL')

    if not backend_url:
        logging.error("BACKEND_API_URL 환경 변수가 설정되지 않았습니다.")
        return

    # 2. 백엔드 API에 POST 요청을 보내 뉴스 수집/분석 작업을 시작시킵니다.
    try:
        # 헤더를 추가하여 요청의 출처를 명확히 할 수 있습니다 (선택 사항).
        headers = {'User-Agent': 'Azure-Function-Timer-Trigger'}
        response = requests.post(backend_url, headers=headers, timeout=30) # 30초 응답 시간 제한
        
        # 요청이 실패하면 (상태 코드가 200번대가 아니면) 에러를 발생시킵니다.
        response.raise_for_status() 
        
        logging.info(f"성공적으로 백엔드 작업을 트리거했습니다. 상태 코드: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"백엔드 작업 트리거에 실패했습니다: {e}")
