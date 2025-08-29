# test.py

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask # <-- Flask 임포트

app = Flask(__name__) # <-- Flask 앱 초기화

# '/' 주소로 접속하면 run_selenium_test 함수를 실행
@app.route("/")
def run_selenium_test():
    google_news_url = "https://news.google.com/rss/articles/CBMia0FVX3lxTFA4MHZYcEhfWks5VERFY2M0eEV4V0VlU1B1TWFNTnhjV280djlGaDZlTlJNQWhPeHgxZjdqTDJhMkdqMG5HMFlqaDlBN2F4WWpIaVp4YWpMM2hDaFBwM1VielNTLUpQSTczMm5B?oc=5"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

    driver = None # finally 블록에서 사용하기 위해 미리 선언
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        print("Selenium 브라우저로 주소에 접속합니다...")
        driver.get(google_news_url)
        
        time.sleep(5) 
        
        original_url = driver.current_url

        print("\n경유 주소:", google_news_url)
        print("찾아낸 원문 기사 주소:", original_url)

        # 웹 브라우저에 결과를 보여줌
        return f"<h1>Original URL Found:</h1><p>{original_url}</p>"

    except Exception as e:
        return f"<h1>An error occurred:</h1><p>{e}</p>"

    finally:
        if driver:
            driver.quit()

# 이 파일이 직접 실행될 때 개발용 서버를 켭니다 (로컬 테스트용)
if __name__ == "__main__":
    app.run()
