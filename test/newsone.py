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
import asyncio
from playwright.async_api import async_playwright

# ================================
# 1. 사용자 설정
# ================================
user_selected_sources = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]
user_follow_categories = ["여행"]

# ================================
# 2. Azure AI 서비스 설정 (원본 값으로 복원)
# ================================
# --- Azure AI 번역기(Translator) 설정 ---
translator_key = "5NuWjUHv52i3letxBdeZw1V46HADYfjoUdUc8aJqBm38uBSl16u4JQQJ99BHACNns7RXJ3w3AAAbACOG8bu6"
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"
translator_location = "KoreaCentral"

# ================================
# 3. Azure OpenAI 초기화 (원본 값으로 복원)
# ================================
endpoint = "https://newscheck2.openai.azure.com/"
deployment = "gpt-4o"
subscription_key = "Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53"
api_version = "2025-01-01-preview"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version=api_version,
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
# 4-1. UI 번역 텍스트
# ================================
ui_texts = {
    'ko': {'reliability_label': '신뢰도', 'high': '높음', 'medium': '보통', 'low': '낮음'},
    'en': {'reliability_label': 'Reliability', 'high': 'High', 'medium': 'Medium', 'low': 'Low'},
    'ja': {'reliability_label': '信頼度', 'high': '高い', 'medium': '普通', 'low': '低い'},
    'fr': {'reliability_label': 'Fiabilité', 'high': 'Élevée', 'medium': 'Moyenne', 'low': 'Faible'},
    'zh-Hans': {'reliability_label': '可信度', 'high': '高', 'medium': '中', 'low': '低'}
}

# ====================================================================
# 5. 원문/이미지 주소 추출 함수 (Playwright를 사용하여 JS 리다이렉트 완벽 해결)
# ====================================================================
async def get_original_article_info_async(google_news_url):
    print(f"  -> [주소 변환 시도] 구글 뉴스 URL: {google_news_url}")
    original_url = google_news_url
    image_url = None
    
    try:
        async with async_playwright() as p:
            # Headless Chromium 브라우저 실행 (서버 환경을 위해 --no-sandbox 옵션 추가)
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = await browser.new_page()
            
            # 구글 뉴스 URL로 이동 (30초 타임아웃)
            await page.goto(google_news_url, timeout=30000)
            
            # 자바스크립트 리다이렉션이 완료될 시간을 벌어주기 위해 잠시 대기
            await page.wait_for_timeout(3000)
            
            # 최종적으로 정착한 페이지의 URL과 콘텐츠 가져오기
            original_url = page.url
            content = await page.content()
            
            print(f"  -> [변환 완료] 원문 주소: {original_url}")
            
            # 이미지 태그 검색
            soup = BeautifulSoup(content, 'html.parser')
            image_tag = soup.find('meta', property='og:image')
            
            if image_tag and image_tag.get('content'):
                image_url = image_tag['content']
                print("  -> 이미지 주소 찾음!")
            else:
                print("  [알림] 이 페이지에는 og:image 태그가 없습니다.")
            
            await browser.close()

    except Exception as e:
        print(f"  [오류] Playwright 처리 중 오류 발생: {e}")
            
    return {'original_url': original_url, 'image_url': image_url}

# 기존 동기식 코드와 호환을 위한 래퍼(wrapper) 함수
def get_original_article_info(google_news_url):
    # 이벤트 루프를 가져오거나 새로 생성하여 실행
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(get_original_article_info_async(google_news_url))


# ================================
# 5-1. 기사 본문 수집 함수
# ================================
def scrape_article_body(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article_tag = soup.find('article')
        if not article_tag:
            selectors = ['#articleBodyContents', '#article_body', '.article_body', '#dic_area']
            for selector in selectors:
                article_tag = soup.select_one(selector)
                if article_tag: break
        if article_tag:
            paragraphs = article_tag.find_all('p')
            if not paragraphs: paragraphs = article_tag.find_all('div')
            body_text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            if len(body_text) > 50:
                print("  -> 본문 수집 성공!")
                return body_text
        print("  [알림] 기사 본문을 찾을 수 없거나 내용이 너무 짧습니다.")
        return None
    except Exception as e:
        print(f"  [오류] 본문 수집 중 오류 발생: {e}")
        return None

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
            body_text = None
            if "news.google.com" not in article_info['original_url']:
                body_text = scrape_article_body(article_info['original_url'])
            
            articles.append({
                'title': entry.title,
                'link': article_info['original_url'],
                'image_url': article_info['image_url'],
                'source': source.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': body_text if body_text else entry.title
            })
    return articles

def gpt_evaluate(article_text, selected_sources):
    prompt_text = f"당신은 뉴스 요약 도우미입니다.\n사용자가 선택한 언론사: {', '.join(selected_sources)}\n\n아래 뉴스 제목 또는 본문을 기반으로:\n1) 3줄로 요약\n2) 선택한 언론사와 핵심 주장 비교\n3) 신뢰도 등급 출력 (반드시 아래 형식만 사용):\n    신뢰도: 높음 / 보통 / 낮음\n\n신뢰도 평가 기준:\n- 주요 언론사(조선일보, 한겨레, 중앙일보, 동아일보, 경향신문) → 높음\n- 제목만 존재하거나 일부 정보만 있는 경우 → 보통\n- 근거 부족/선정적/출처 불분명 → 낮음\n\n⚠️ 출력 형식을 반드시 지켜주세요. 다른 말은 절대 추가하지 마세요."
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
    headers = {'Ocp-Apim-Subscription-Key': translator_key, 'Ocp-Apim-Subscription-Region': translator_location, 'Content-type': 'application/json', 'X-ClientTraceId': str(uuid.uuid4())}
    params = {'api-version': '3.0', 'from': 'ko', 'to': target_languages}
    body = [{'text': text_to_translate}]
    try:
        response = requests.post(f"{translator_endpoint}/translate", params=params, headers=headers, json=body)
        response.raise_for_status()
        translations = response.json()
        return {t['to']: t['text'] for t in translations[0]['translations']}
    except Exception as e:
        print(f"Azure 번역 API 오류: {e}")
        return {lang: "번역 오류" for lang in target_languages}

# ================================
# 8. HTML 저장 함수 (수정됨)
# ================================
def save_news_with_translations(main_category, sub_category, articles):
    main_path = os.path.join(save_path, main_category)
    os.makedirs(main_path, exist_ok=True)
    file_name = f"{sub_category.replace('/', '_')}_news.html"
    full_path = os.path.join(main_path, file_name)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='utf-8'><title>뉴스 요약</title><style>body{font-family:'Malgun Gothic',sans-serif;margin:20px;line-height:1.6}.article-block{border-bottom:1px solid #ddd;padding-bottom:15px;margin-bottom:15px}.lang-buttons{margin-bottom:10px}.lang-buttons button{padding:8px 12px;cursor:pointer;border:1px solid #ccc;background-color:#f0f0f0;margin-right:5px;border-radius:5px}.lang-buttons button.active{background-color:#3498db;color:white;border-color:#3498db}.content-wrapper .content{display:none}.content-wrapper .content.active{display:block}.summary{background-color:#f8f9f9;border-left:4px solid #3498db;padding:10px;margin-top:5px}.reliability{font-weight:bold;padding:3px 8px;border-radius:5px;color:white;display:inline-block;margin-left:10px}.high{background-color:#2ecc71}.medium{background-color:#f39c12}.low{background-color:#e74c3c}.article-image{max-width:100%;height:auto;border-radius:8px;margin-bottom:10px;object-fit:cover;max-height:400px}.no-image-text{color:#888;font-style:italic;margin-bottom:10px;display:block}</style></head><body>")
        f.write(f"<h1>{main_category} - {sub_category} 뉴스</h1>")
        f.write('<div class="lang-buttons"><strong>전체 언어 변경:</strong><button onclick="changeAllLanguages(\'ko\')" class="active">한국어</button><button onclick="changeAllLanguages(\'en\')">English</button><button onclick="changeAllLanguages(\'ja\')">日本語</button><button onclick="changeAllLanguages(\'zh-Hans\')">中文(简体)</button><button onclick="changeAllLanguages(\'fr\')">Français</button></div><hr>')
        
        for i, article in enumerate(articles):
            f.write(f'<div class="article-block" id="article-{i}">')
            if article.get('image_url'):
                f.write(f"<img src='{article['image_url']}' alt='기사 대표 이미지' class='article-image' onerror='this.style.display=\"none\"'>")
            else:
                f.write("<span class='no-image-text'>[이미지 없음]</span>")
            
            f.write(f"<p><b>언론사:</b> {article['source']} | <b>발행 시간:</b> {article['date']}</p><div class='content-wrapper'>")
            
            for lang, content in article['translations'].items():
                active_class = "active" if lang == 'ko' else ""
                title = content['title']
                summary_html = content['summary_html']
                
                f.write(f'<div class="content {lang} {active_class}">')
                f.write(f'<h3><a href=\'{article["link"]}\' target=\'blank\'>{title}</a></h3>')
                f.write(summary_html)
                f.write('</div>')
            
            f.write('</div></div>')
        f.write('<script>function changeAllLanguages(lang){document.querySelectorAll(".lang-buttons button").forEach(b=>b.classList.remove("active"));document.querySelector(`.lang-buttons button[onclick="changeAllLanguages(\'${lang}\')"]`).classList.add("active");document.querySelectorAll(".article-block").forEach(article=>{article.querySelectorAll(".content").forEach(c=>c.classList.remove("active"));const target=article.querySelector(`.content.${lang}`);if(target)target.classList.add("active")})}</script></body></html>')

# ================================
# 9. 메인 실행 루프 (최종 수정)
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
            
            # 1. 번역할 텍스트 준비 및 API 호출
            text_to_translate = f"{article['title']}\n{summary_text}"
            azure_translations = translate_with_azure(text_to_translate, target_languages)

            # 2. 모든 언어의 제목과 요약 내용을 담을 딕셔너리 준비
            all_content = {'ko': {'title': article['title'], 'summary': summary_text}}
            for lang, translated_full_text in azure_translations.items():
                parts = translated_full_text.split('\n', 1)
                all_content[lang] = {
                    'title': parts[0],
                    'summary': parts[1] if len(parts) > 1 else ""
                }
            
            # 3. 신뢰도 값에 대한 키와 CSS 클래스 설정
            reliability_key_map = {"높음": "high", "보통": "medium", "낮음": "low"}
            reliability_key = reliability_key_map.get(reliability, "low")
            reliability_class = reliability_key
            
            # 4. 각 언어별로 번역된 UI 텍스트를 사용하여 HTML 생성
            final_translations = {}
            for lang, content in all_content.items():
                # ui_texts 딕셔너리에서 현재 언어에 맞는 텍스트 가져오기
                reliability_label = ui_texts[lang]['reliability_label']
                translated_reliability_value = ui_texts[lang][reliability_key]
                
                # 번역된 텍스트로 summary_html 생성
                summary_html = (f"<div class='summary'>{content['summary'].replace('\n', '<br>')}<br>"
                                f"<span class='reliability {reliability_class}'>"
                                f"{reliability_label}: {translated_reliability_value}</span></div>")
                
                final_translations[lang] = {
                    'title': content['title'],
                    'summary_html': summary_html
                }

            article_data = {
                'link': article['link'], 
                'image_url': article['image_url'], 
                'source': article['source'], 
                'date': article['date'],
                'translations': final_translations
            }
            
            processed_articles.append(article_data)
        
        save_news_with_translations(main_category, sub_category, processed_articles)
        print(f"  -> {len(processed_articles)}개 뉴스 저장 완료.")

print("\n🎉 모든 뉴스 수집, 평가 및 번역 완료!")