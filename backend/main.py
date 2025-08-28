# ================================
# 0. 라이브러리 임포트
# ================================
import feedparser  # RSS 피드를 파싱(분석)하기 위한 라이브러리
import time  # 프로그램 실행 중 잠시 멈추거나(sleep) 시간 관련 작업을 위한 라이브러리
import os  # 운영체제와 상호작용하기 위한 라이브러리 (폴더 생성, 파일 경로 등)
from datetime import datetime, timedelta  # 날짜와 시간을 다루기 위한 라이브러리
from urllib.parse import quote  # URL에 한글 같은 문자를 안전하게 포함시키기 위한 라이브러리
from openai import AzureOpenAI  # Azure의 OpenAI 서비스를 사용하기 위한 라이브러리
import re  # 정규 표현식을 사용해 문자열에서 특정 패턴을 찾기 위한 라이브러리
import requests  # 웹사이트에 HTTP 요청을 보내기 위한 라이브러리
import uuid  # 고유한 ID를 생성하기 위한 라이브러리 (번역 요청 시 추적 ID로 사용)
from bs4 import BeautifulSoup  # HTML 및 XML 파일에서 데이터를 쉽게 추출하기 위한 라이브러리
from selenium import webdriver  # 웹 브라우저를 자동으로 제어하기 위한 라이브러리
from selenium.webdriver.chrome.service import Service  # 셀레니움에서 크롬 드라이버 서비스를 관리
from selenium.webdriver.chrome.options import Options  # 크롬 브라우저의 옵션(예: 헤드리스 모드)을 설정
from selenium.webdriver.support.ui import WebDriverWait  # 셀레니움에서 특정 조건이 만족될 때까지 기다리도록 설정

# ================================
# 1. 사용자 설정
# ================================
# GPT가 신뢰도를 평가할 때 기준으로 삼을 주요 언론사 목록
user_selected_sources = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]
# 사용자가 구독하여 뉴스를 수집할 메인 카테고리 목록
user_follow_categories = ["여행"]

# ================================
# 2. Azure AI 서비스 설정
# ================================
# --- Azure AI 번역기(Translator) 설정 ---
translator_key = "..."  # Azure 번역 서비스의 구독 키
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"  # Azure 번역 서비스의 엔드포인트 주소
translator_location = "KoreaCentral"  # Azure 번역 서비스의 리소스 지역

# ================================
# 3. Azure OpenAI 초기화
# ================================
endpoint = "https://newscheck2.openai.azure.com/"  # Azure OpenAI 서비스의 엔드포인트 주소
deployment = "gpt-4o"  # Azure에 배포한 모델의 '배포 이름'
subscription_key = "..."  # Azure OpenAI 서비스의 구독 키
api_version = "2025-01-01-preview"  # 사용할 API의 버전

# 위 설정값들을 사용하여 Azure OpenAI 서비스에 연결할 수 있는 클라이언트 객체를 생성
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version=api_version,
)

# ================================
# 4. 전체 뉴스/카테고리
# ================================
# 수집 대상이 될 전체 언론사 목록
all_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제'
]
# 수집할 뉴스의 대분류와 소분류 목록을 딕셔너리 형태로 정의
categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계'],
    '여행': ['국내 여행']
}
MAX_ARTICLES_PER_CATEGORY = 100  # 각 카테고리별로 수집할 최대 기사 수
save_path = 'C:/Users/admin/Desktop/news/test1/output'  # 결과 HTML 파일이 저장될 경로
one_month_ago = datetime.now() - timedelta(days=30)  # 한 달 전 날짜를 계산 (이보다 오래된 뉴스는 수집 안 함)
os.makedirs(save_path, exist_ok=True)  # 저장 경로에 폴더가 없으면 자동으로 생성

# ================================
# 5. 원문/이미지 주소 추출 함수 (WebDriverWait 적용)
# ================================
# 구글 뉴스 링크를 입력받아 실제 원문 기사 주소와 대표 이미지 주소를 찾아내는 함수
def get_original_article_info(google_news_url):
    print(f"  -> [변환 시도] 기존 주소: {google_news_url}")  # 현재 처리 중인 구글 뉴스 URL 출력
    chrome_options = Options()  # 크롬 브라우저 옵션 설정 객체 생성
    chrome_options.add_argument("--headless")  # 브라우저 창을 실제로 띄우지 않는 헤드리스 모드로 실행
    chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (헤드리스 모드에서 안정성 향상)
    chrome_options.add_argument("user-agent=...")  # User-Agent 값을 설정하여 봇으로 인식되는 것을 방지
    service = Service()  # 크롬 드라이버 서비스 객체 생성
    driver = webdriver.Chrome(service=service, options=chrome_options)  # 설정된 옵션으로 크롬 드라이버 실행
    original_url, image_url = google_news_url, None  # 초기값 설정
    try:  # 오류 발생 가능성이 있는 코드를 try 블록 안에 작성
        driver.get(google_news_url)  # 셀레니움으로 구글 뉴스 URL 접속
        # 페이지가 리디렉션되어 현재 URL에 "news.google.com"이 없을 때까지 최대 15초간 기다림
        WebDriverWait(driver, 15).until(lambda d: "news.google.com" not in d.current_url)
        original_url = driver.current_url  # 리디렉션이 완료된 최종 URL을 저장
        print(f"  -> [변환 완료] 원문 주소: {original_url}")  # 변환된 원문 주소 출력
        soup = BeautifulSoup(driver.page_source, 'html.parser')  # 페이지의 HTML 소스를 BeautifulSoup으로 파싱
        # HTML의 <meta> 태그 중 property 속성이 'og:image'인 것을 찾음 (대표 이미지를 나타냄)
        image_tag = soup.find('meta', property='og:image')
        if image_tag and image_tag.get('content'):  # 이미지 태그와 그 내용이 존재하면
            image_url = image_tag['content']  # content 속성값(이미지 URL)을 저장
            print("  -> 이미지 주소 찾음!")
        else:  # 이미지 태그가 없으면
            print("  [알림] 이 페이지에는 og:image 태그가 없습니다.")
    except Exception as e:  # try 블록에서 오류 발생 시
        print(f"  [오류] 작업 중 오류 발생 (타임아웃 또는 기타): {e}")  # 오류 메시지 출력
        original_url = driver.current_url  # 오류 발생 시점의 URL을 저장
        print(f"  -> [오류 시점 주소] {original_url}")
    finally:  # 오류 발생 여부와 상관없이 항상 실행
        driver.quit()  # 크롬 드라이버 종료
    return {'original_url': original_url, 'image_url': image_url}  # 원문 주소와 이미지 주소를 딕셔너리로 반환

# ================================
# 5-1. 기사 본문 수집 함수
# ================================
# 기사 URL을 입력받아 웹페이지에서 본문 텍스트를 추출(스크래핑)하는 함수
def scrape_article_body(url):
    try:  # 오류 발생 가능성이 있는 코드를 try 블록 안에 작성
        headers = {'User-Agent': '...'}  # 봇으로 인식되지 않도록 User-Agent 설정
        # requests 라이브러리로 URL에 접속하여 페이지 내용을 가져옴 (타임아웃 10초)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 요청이 실패하면(200번대 코드가 아니면) 오류를 발생시킴
        soup = BeautifulSoup(response.text, 'html.parser')  # 페이지 내용을 BeautifulSoup으로 파싱
        article_tag = soup.find('article')  # HTML의 <article> 태그를 찾음 (보통 기사 본문을 감싸고 있음)
        if not article_tag:  # <article> 태그를 찾지 못했다면
            # 다른 언론사에서 흔히 사용하는 id나 class 이름으로 다시 검색
            selectors = ['#articleBodyContents', '#article_body', '.article_body', '#dic_area']
            for selector in selectors:
                article_tag = soup.select_one(selector)
                if article_tag: break  # 찾으면 반복 중단
        if article_tag:  # 본문 컨테이너 태그를 찾았다면
            paragraphs = article_tag.find_all('p')  # 그 안에서 모든 <p>(문단) 태그를 찾음
            if not paragraphs: paragraphs = article_tag.find_all('div')  # <p>가 없으면 <div> 태그를 대신 찾음
            # 모든 문단의 텍스트를 하나로 합침 (앞뒤 공백 제거, 빈 문단 제외)
            body_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            if len(body_text) > 50:  # 본문 길이가 50자 이상이면
                print("  -> 본문 수집 성공!")
                return body_text  # 수집한 텍스트를 반환
        print("  [알림] 기사 본문을 찾을 수 없거나 내용이 너무 짧습니다.")
        return None  # 본문 수집에 실패하면 None을 반환
    except Exception as e:  # 오류 발생 시
        print(f"  [오류] 본문 수집 중 오류 발생: {e}")
        return None  # 오류 발생 시 None을 반환

# ================================
# 6. 뉴스 수집 및 GPT 평가 함수
# ================================
# 특정 소분류 키워드로 구글 뉴스 RSS에서 기사 목록을 가져오는 함수
def fetch_news(sub_category):
    encoded_keyword = quote(sub_category)  # 한글 키워드를 URL에 사용할 수 있도록 인코딩
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"  # 구글 뉴스 RSS 주소 생성
    feed = feedparser.parse(news_url)  # feedparser로 RSS 피드를 분석
    articles = []  # 수집한 기사 정보를 저장할 리스트
    for entry in feed.entries:  # RSS 피드에 있는 각 기사(entry)에 대해 반복
        if len(articles) >= MAX_ARTICLES_PER_CATEGORY: break  # 최대 수집 개수에 도달하면 중단
        source = getattr(entry, 'source', None)  # 기사의 출처(언론사) 정보를 가져옴
        if source and source.title in all_sources:  # 출처가 있고, 우리가 정한 언론사 목록에 포함되어 있다면
            published_time = entry.get('published_parsed')  # 기사 발행 시간을 가져옴
            if not published_time: continue  # 발행 시간이 없으면 건너뜀
            article_date = datetime.fromtimestamp(time.mktime(published_time))  # 발행 시간을 datetime 객체로 변환
            if article_date < one_month_ago: continue  # 너무 오래된 기사(한 달 이전)는 건너뜀
            print(f"Processing '{entry.title[:30]}...'")  # 처리 중인 기사 제목 출력
            article_info = get_original_article_info(entry.link)  # 원문 주소와 이미지 주소 추출
            body_text = None  # 본문 텍스트 초기화
            if "news.google.com" not in article_info['original_url']:  # 원문 주소 변환에 성공했다면
                body_text = scrape_article_body(article_info['original_url'])  # 본문 텍스트 수집
            articles.append({  # 수집한 기사 정보를 딕셔너리 형태로 리스트에 추가
                'title': entry.title,
                'link': article_info['original_url'],
                'image_url': article_info['image_url'],
                'source': source.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': body_text if body_text else entry.title  # 본문 수집 성공 시 본문을, 실패 시 제목을 content로 사용
            })
    return articles  # 기사 정보가 담긴 리스트를 반환

# 기사 내용(텍스트)을 받아 GPT 모델에 요약 및 신뢰도 평가를 요청하는 함수
def gpt_evaluate(article_text, selected_sources):
    # GPT에 보낼 프롬프트(명령어)를 생성. 역할, 요구사항, 형식 등을 자세히 지정
    prompt_text = f"..."
    # GPT에 전달할 메시지 목록을 생성. 시스템 역할, 사용자 프롬프트, 실제 기사 내용으로 구성
    messages = [{"role": "system", "content": "..."}, {"role": "user", "content": prompt_text}, {"role": "user", "content": article_text}]
    try:  # 오류 발생 가능성이 있는 코드를 try 블록 안에 작성
        # 설정된 클라이언트를 통해 Azure OpenAI에 채팅 완료(chat completions) 요청을 보냄
        completion = client.chat.completions.create(model=deployment, messages=messages, max_completion_tokens=1024)
        # AI가 생성한 답변 텍스트를 반환 (앞뒤 공백 제거)
        return completion.choices[0].message.content.strip()
    except Exception as e:  # 오류 발생 시
        return f"GPT 평가 오류: {e}"  # 오류 메시지를 포함한 문자열을 반환

# ================================
# 7. Azure 번역 함수
# ================================
# 텍스트를 받아 지정된 여러 언어로 번역하는 함수
def translate_with_azure(text_to_translate, target_languages):
    headers = {'Ocp-Apim-Subscription-Key': translator_key, ...}  # 요청 헤더에 인증 키 등을 포함
    params = {'api-version': '3.0', 'from': 'ko', 'to': target_languages}  # 요청 파라미터에 API 버전, 출발/도착 언어 등을 설정
    body = [{'text': text_to_translate}]  # 요청 본문에 번역할 텍스트를 포함
    try:  # 오류 발생 가능성이 있는 코드를 try 블록 안에 작성
        # requests 라이브러리로 Azure 번역 API에 POST 요청을 보냄
        response = requests.post(f"{translator_endpoint}/translate", params=params, headers=headers, json=body)
        response.raise_for_status()  # HTTP 요청 실패 시 오류 발생
        translations = response.json()  # 응답받은 JSON 데이터를 파싱
        # 번역 결과를 {언어코드: 번역된 텍스트} 형태의 딕셔너리로 만들어 반환
        return {t['to']: t['text'] for t in translations[0]['translations']}
    except Exception as e:  # 오류 발생 시
        print(f"Azure 번역 API 오류: {e}")
        return {lang: "번역 오류" for lang in target_languages}  # 각 언어에 대해 "번역 오류" 메시지를 담은 딕셔너리 반환

# ================================
# 8. HTML 저장 함수
# ================================
# 수집하고 처리한 기사 목록을 받아 하나의 HTML 파일로 저장하는 함수
def save_news_with_translations(main_category, sub_category, articles):
    main_path = os.path.join(save_path, main_category)  # 대분류 폴더 경로 생성
    os.makedirs(main_path, exist_ok=True)  # 폴더가 없으면 생성
    file_name = f"{sub_category.replace('/', '_')}_news.html"  # 파일 이름 설정 (슬래시 문자는 언더바로 변경)
    full_path = os.path.join(main_path, file_name)  # 전체 파일 경로 생성
    with open(full_path, 'w', encoding='utf-8') as f:  # 파일을 쓰기 모드('w')와 UTF-8 인코딩으로 열기
        # HTML의 기본 구조와 CSS 스타일 시트 작성
        f.write("<html><head>...</head><body>")
        f.write(f"<h1>{main_category} - {sub_category} 뉴스</h1>")  # 페이지 제목 작성

        # 전체 언어를 한 번에 바꿀 수 있는 버튼들 생성
        f.write('<div class="lang-buttons">...</div><hr>')

        for i, article in enumerate(articles):  # 각 기사에 대해 반복
            f.write(f'<div class="article-block" id="article-{i}">')  # 기사 하나를 감싸는 div 블록 생성
            if article.get('image_url'):  # 이미지 URL이 있다면
                f.write(f"<img src='{article['image_url']}' ...>")  # <img> 태그로 이미지 표시
            else:  # 이미지 URL이 없다면
                f.write("<span class='no-image-text'>[이미지 없음]</span>")  # 텍스트로 표시
            
            f.write(f"<p><b>언론사:</b> {article['source']} | <b>발행 시간:</b> {article['date']}</p>")  # 언론사와 발행 시간 표시
            f.write('<div class="content-wrapper">')  # 제목과 요약을 감싸는 div 생성
            for lang, content in article['translations'].items():  # 각 언어별 번역 내용에 대해 반복
                active_class = "active" if lang == 'ko' else ""  # 한국어 콘텐츠는 기본으로 보이도록 'active' 클래스 추가
                # ... 언어별 제목과 요약 내용을 HTML 구조에 맞게 작성 ...
            f.write('</div></div>')

        # 언어 변경 버튼이 작동하도록 하는 자바스크립트 코드 작성
        f.write('<script>function changeAllLanguages(lang){...}</script>')
        f.write("</body></html>")  # HTML 파일 닫기

# ================================
# 9. 메인 실행 루프
# ================================
target_languages = ['en', 'ja', 'fr', 'zh-Hans']  # 번역할 목표 언어 목록

# `categories` 딕셔너리에 정의된 모든 카테고리에 대해 반복 실행
for main_category, sub_categories in categories.items():
    if main_category not in user_follow_categories: continue  # 사용자가 선택한 카테고리가 아니면 건너뜀
    for sub_category in sub_categories:  # 대분류 안의 소분류에 대해 반복
        print(f"[{main_category}] {sub_category} 뉴스 수집 중...")  # 현재 수집 중인 카테고리 출력
        articles = fetch_news(sub_category)  # 해당 소분류의 뉴스 기사들을 수집
        if not articles:  # 수집된 기사가 없으면
            print("  -> 수집된 뉴스가 없습니다.")
            continue  # 다음 소분류로 넘어감
        processed_articles = []  # 처리된 기사 정보를 저장할 리스트
        for article in articles:  # 수집된 각 기사에 대해 반복
            print(f"  - '{article['title'][:30]}...' GPT 평가 및 번역 중...")  # 처리 중인 기사 제목 출력

            # 기사 내용(content)을 GPT에 보내 요약 및 평가를 받음
            evaluation_text = gpt_evaluate(article['content'], user_selected_sources)

            # [디버깅 코드] AI의 실제 응답을 터미널에 그대로 출력
            print("---------- GPT Raw Response ----------")
            print(evaluation_text)
            print("------------------------------------")

            time.sleep(1)  # API에 너무 많은 요청을 짧은 시간에 보내지 않도록 1초 대기
            # 정규 표현식을 사용해 GPT 응답에서 '1)'로 시작하는 요약 부분을 추출
            summary_match = re.search(r'1\)(.*?)(?=2\)|\Z)', evaluation_text, re.DOTALL)
            # 정규 표현식을 사용해 GPT 응답에서 '신뢰도:' 부분을 추출
            reliability_match = re.search(r'신뢰도:\s*(높음|보통|낮음)', evaluation_text)
            # 요약 추출에 성공하면 그 내용을, 실패하면 "요약 정보 없음"을 저장
            summary_text = summary_match.group(1).strip() if summary_match else "요약 정보 없음"
            # 신뢰도 추출에 성공하면 그 내용을, 실패하면 "알 수 없음"을 저장
            reliability = reliability_match.group(1).strip() if reliability_match else "알 수 없음"
            # 기사 제목과 요약문을 Azure 번역 서비스에 보내 번역
            azure_translations = translate_with_azure(f"{article['title']}\n{summary_text}", target_languages)
            # 번역된 결과에서 제목 부분만 추출
            translated_titles = {lang: trans_text.split('\n', 1)[0] for lang, trans_text in azure_translations.items()}
            # 신뢰도 등급에 따라 HTML에서 사용할 CSS 클래스 이름을 결정
            reliability_class = {"높음": "high", "보통": "medium"}.get(reliability, "low")
            # 요약과 신뢰도 정보를 포함하는 HTML 조각을 생성
            summary_html = f"<div class='summary'>{summary_text.replace('\n', '<br>')}<span class='reliability {reliability_class}'>신뢰도: {reliability}</span></div>"
            # 최종적으로 HTML 파일에 저장할 모든 기사 데이터를 딕셔너리 형태로 정리
            article_data = {
                'link': article['link'], 'image_url': article['image_url'], 'source': article['source'], 'date': article['date'],
                'translations': {
                    'ko': {'title': article['title'], 'summary_html': summary_html},
                    'en': translated_titles.get('en', "번역 오류"), 'ja': translated_titles.get('ja', "번역 오류"),
                    'fr': translated_titles.get('fr', "번역 오류"), 'zh-Hans': translated_titles.get('zh-Hans', "번역 오류")
                }
            }
            processed_articles.append(article_data)  # 처리된 기사 데이터를 리스트에 추가
        # 해당 소분류의 모든 기사 처리가 끝나면 HTML 파일로 저장
        save_news_with_translations(main_category, sub_category, processed_articles)
        print(f"  -> {len(processed_articles)}개 뉴스 저장 완료.")
print("\n🎉 모든 뉴스 수집, 평가 및 번역 완료!")  # 모든 작업이 끝나면 완료 메시지 출력
