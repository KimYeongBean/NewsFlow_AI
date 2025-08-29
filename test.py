import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

google_news_url = "https://news.google.com/rss/articles/CBMia0FVX3lxTFA4MHZYcEhfWks5VERFY2M0eEV4V0VlU1B1TWFNTnhjV280djlGaDZlTlJNQWhPeHgxZjdqTDJhMkdqMG5HMFlqaDlBN2F4WWpIaVp4YWpMM2hDaFBwM1VielNTLUpQSTczMm5B?oc=5"

# 브라우저 창이 뜨지 않는 headless 모드로 실행
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


try:
    # 최신 크롬 드라이버를 자동으로 관리
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(20) # 페이지 로딩 타임아웃 20초 설정

    print("Selenium 브라우저로 주소에 접속합니다...")
    driver.get(google_news_url)
    
    # 자바스크립트 리디렉션이 완료될 시간을 충분히 기다립니다.
    time.sleep(5) 
    
    # 최종적으로 도달한 페이지의 URL을 가져옵니다.
    original_url = driver.current_url

    print("\n경유 주소:", google_news_url)
    print("찾아낸 원문 기사 주소:", original_url)

finally:
    if 'driver' in locals():
        driver.quit() # 사용 후 반드시 브라우저를 종료합니다.