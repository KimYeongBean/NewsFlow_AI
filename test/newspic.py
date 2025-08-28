# ================================
# 0. 라이브러리 임포트
# ================================
import feedparser
import time
import os
from datetime import datetime, timedelta
from urllib.parse import quote
from openai import AzureOpenAI
import re
import requests
import uuid
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# ================================
# 1. 사용자 설정
# ================================
user_selected_sources = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]
user_follow_categories = ["여행"]

# ================================
# 2. Azure AI 서비스 설정
# ================================
# --- Azure AI 번역기(Translator) 설정 ---
translator_key = "5NuWjUHv52i3letxBdeZw1V46HADYfjoUdUc8aJqBm38uBSl16u4JQQJ99BHACNns7RXJ3w3AAAbACOG8bu6"
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"
translator_location = "KoreaCentral"

# ================================
# 3. Azure OpenAI 초기화
# ================================
endpoint = "https://newscheck2.openai.azure.com/"
deployment = "gpt-5-nano"
subscription_key = "Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2025-01-01-preview",
)

# ================================
# 4. 전체 뉴스/카테고리
# ================================
all_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제'
]
categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계'],
    '여행': ['국내 여행']
}
MAX_ARTICLES_PER_CATEGORY = 100
save_path = 'C:/Users/admin/Desktop/news/test1/output'
one_month_ago = datetime.now() - timedelta(days=30)
os.makedirs(save_path, exist_ok=True)

# ================================
# 5. 원문/이미지 주소 추출 함수 (WebDriverWait 적용)
# ================================
def get_original_article_info(google_news_url):
    """
    Selenium의 WebDriverWait를 이용해 URL이 실제로 변경될 때까지 기다린 후
    원문 주소와 이미지 주소를 가져옵니다.
    """
    print(f"  -> [변환 시도] 기존 주소: {google_news_url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    original_url = google_news_url
    image_url = None

    try:
        driver.get(google_news_url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(lambda driver: "news.google.com" not in driver.current_url)
        
        original_url = driver.current_url
        print(f"  -> [변환 완료] 원문 주소: {original_url}")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_tag = soup.find('meta', property='og:image')
        
        if image_tag and image_tag.get('content'):
            image_url = image_tag['content']
            print("  -> 이미지 주소 찾음!")
        else:
            print("  [알림] 이 페이지에는 og:image 태그가 없습니다.")

    except Exception as e:
        print(f"  [오류] 작업 중 오류 발생 (타임아웃 또는 기타): {e}")
        original_url = driver.current_url
        print(f"  -> [오류 시점 주소] {original_url}")
    finally:
        driver.quit()
        
    return {'original_url': original_url, 'image_url': image_url}

# ================================
# 6. 뉴스 수집 및 GPT 평가 함수
# ================================
def fetch_news(sub_category):
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
    feed = feedparser.parse(news_url)
    articles = []
    for entry in feed.entries:
        if len(articles) >= MAX_ARTICLES_PER_CATEGORY: break
        source = getattr(entry, 'source', None)
        if source and source.title in all_sources:
            published_time = entry.get('published_parsed')
            if not published_time: continue
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date < one_month_ago: continue
            
            print(f"Processing '{entry.title[:30]}...'")
            article_info = get_original_article_info(entry.link)

            articles.append({
                'title': entry.title,
                'link': article_info['original_url'],
                'image_url': article_info['image_url'],
                'source': source.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': entry.title
            })
    return articles

def gpt_evaluate(article_text, selected_sources):
    prompt_text = f"""
당신은 뉴스 요약 도우미입니다.
사용자가 선택한 언론사: {', '.join(selected_sources)}

아래 뉴스 제목 또는 본문을 기반으로:
1) 3줄로 요약
2) 선택한 언론사와 핵심 주장 비교
3) 신뢰도 등급 출력 (반드시 아래 형식만 사용):
    신뢰도: 높음 / 보통 / 낮음

신뢰도 평가 기준:
- 주요 언론사(조선일보, 한겨레, 중앙일보, 동아일보, 경향신문) → 높음
- 제목만 존재하거나 일부 정보만 있는 경우 → 보통
- 근거 부족/선정적/출처 불분명 → 낮음

⚠️ 출력 형식을 반드시 지켜주세요.
"""
    messages = [{"role": "system", "content": "너는 뉴스 요약과 언론사 비교, 신뢰도 평가만 간단히 출력하는 도우미야."}, {"role": "user", "content": prompt_text}, {"role": "user", "content": article_text}]
    try:
        completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=1024)
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 평가 오류: {e}"

# ================================
# 7. Azure 번역 함수
# ================================
def translate_with_azure(text_to_translate, target_languages):
    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Ocp-Apim-Subscription-Region': translator_location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    params = { 'api-version': '3.0', 'from': 'ko', 'to': target_languages }
    body = [{'text': text_to_translate}]
    
    try:
        response = requests.post(f"{translator_endpoint}/translate", params=params, headers=headers, json=body)
        response.raise_for_status()
        translations = response.json()
        return {t['to']: t['text'] for t in translations[0]['translations']}
    except requests.exceptions.RequestException as e:
        print(f"Azure 번역 API 오류: {e}")
        return {lang: "번역 오류" for lang in target_languages}

# ================================
# 8. HTML 저장 함수
# ================================
def save_news_with_translations(main_category, sub_category, articles):
    main_path = os.path.join(save_path, main_category)
    os.makedirs(main_path, exist_ok=True)
    file_name = f"{sub_category.replace('/', '_')}_news.html"
    full_path = os.path.join(main_path, file_name)

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='utf-8'><title>뉴스 요약</title>")
        f.write("""
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; margin: 20px; line-height: 1.6; }
            .article-block { border-bottom: 1px solid #ddd; padding-bottom: 15px; margin-bottom: 15px; }
            .lang-buttons { margin-bottom: 10px; }
            .lang-buttons button { padding: 8px 12px; cursor: pointer; border: 1px solid #ccc; background-color: #f0f0f0; margin-right: 5px; border-radius: 5px; }
            .lang-buttons button.active { background-color: #3498db; color: white; border-color: #3498db; }
            .content-wrapper .content { display: none; }
            .content-wrapper .content.active { display: block; }
            .summary { background-color: #f8f9f9; border-left: 4px solid #3498db; padding: 10px; margin-top: 5px; }
            .reliability { font-weight: bold; padding: 3px 8px; border-radius: 5px; color: white; display: inline-block; margin-left: 10px; }
            .high { background-color: #2ecc71; } .medium { background-color: #f39c12; } .low { background-color: #e74c3c; }
            .article-image {
                max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 10px; object-fit: cover; max-height: 400px;
            }
            .no-image-text {
                color: #888; font-style: italic; margin-bottom: 10px; display: block;
            }
        </style>
        </head><body>""")
        f.write(f"<h1>{main_category} - {sub_category} 뉴스</h1>")

        f.write('<div class="lang-buttons"><strong>전체 언어 변경:</strong>')
        f.write('<button onclick="changeAllLanguages(\'ko\')" class="active">한국어</button>')
        f.write('<button onclick="changeAllLanguages(\'en\')">English</button>')
        f.write('<button onclick="changeAllLanguages(\'ja\')">日本語</button>')
        f.write('<button onclick="changeAllLanguages(\'zh-Hans\')">中文(简体)</button>')
        f.write('<button onclick="changeAllLanguages(\'fr\')">Français</button>')
        f.write('</div><hr>')

        for i, article in enumerate(articles):
            f.write(f'<div class="article-block" id="article-{i}">')
            if article.get('image_url'):
                f.write(f"<img src='{article['image_url']}' alt='기사 대표 이미지' class='article-image' onerror='this.style.display=\"none\"'>")
            else:
                f.write("<span class='no-image-text'>[이미지 없음]</span>")
                
            f.write(f"<p><b>언론사:</b> {article['source']} | <b>발행 시간:</b> {article['date']}</p>")
            f.write('<div class="content-wrapper">')
            for lang, content in article['translations'].items():
                active_class = "active" if lang == 'ko' else ""
                if lang == 'ko':
                    title, summary_html = content['title'], content['summary_html']
                else:
                    title, summary_html = content, article['translations']['ko']['summary_html']
                f.write(f'<div class="content {lang} {active_class}">')
                f.write(f"<h3><a href='{article['link']}' target='blank'>{title}</a></h3>")
                if lang == 'ko' and summary_html:
                    f.write(summary_html)
                f.write('</div>')
            f.write('</div></div>')

        f.write('''
        <script>
            function changeAllLanguages(lang) {
                document.querySelectorAll('.lang-buttons button').forEach(b => b.classList.remove('active'));
                document.querySelector(`.lang-buttons button[onclick="changeAllLanguages('${lang}')"]`).classList.add('active');
                document.querySelectorAll('.article-block').forEach(article => {
                    article.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
                    const target = article.querySelector(`.content.${lang}`);
                    if (target) target.classList.add('active');
                });
            }
        </script>''')
        f.write("</body></html>")

# ================================
# 9. 메인 실행 루프
# ================================
target_languages = ['en', 'ja', 'fr', 'zh-Hans']

for main_category, sub_categories in categories.items():
    if main_category not in user_follow_categories: continue
    for sub_category in sub_categories:
        print(f"[{main_category}] {sub_category} 뉴스 수집 중...")
        articles = fetch_news(sub_category)
        if not articles:
            print("  -> 수집된 뉴스가 없습니다.")
            continue
        processed_articles = []
        for article in articles:
            print(f"  - '{article['title'][:30]}...' GPT 평가 및 번역 중...")
            evaluation_text = gpt_evaluate(article['content'], user_selected_sources)
            time.sleep(1)
            summary_match = re.search(r'1\)(.*?)(?=2\)|\Z)', evaluation_text, re.DOTALL)
            reliability_match = re.search(r'신뢰도:\s*(높음|보통|낮음)', evaluation_text)
            summary_text = summary_match.group(1).strip() if summary_match else "요약 정보 없음"
            reliability = reliability_match.group(1).strip() if reliability_match else "알 수 없음"
            azure_translations = translate_with_azure(f"{article['title']}\n{summary_text}", target_languages)
            translated_titles = {lang: trans_text.split('\n', 1)[0] for lang, trans_text in azure_translations.items()}
            reliability_class = {"높음": "high", "보통": "medium"}.get(reliability, "low")
            summary_html = f"<div class='summary'>{summary_text.replace('\n', '<br>')}<span class='reliability {reliability_class}'>신뢰도: {reliability}</span></div>"
            article_data = {
                'link': article['link'], 'image_url': article['image_url'], 'source': article['source'], 'date': article['date'],
                'translations': {
                    'ko': {'title': article['title'], 'summary_html': summary_html},
                    'en': translated_titles.get('en', "번역 오류"), 'ja': translated_titles.get('ja', "번역 오류"),
                    'fr': translated_titles.get('fr', "번역 오류"), 'zh-Hans': translated_titles.get('zh-Hans', "번역 오류")
                }
            }
            processed_articles.append(article_data)
        save_news_with_translations(main_category, sub_category, processed_articles)
        print(f"  -> {len(processed_articles)}개 뉴스 저장 완료.")
print("\n🎉 모든 뉴스 수집, 평가 및 번역 완료!")