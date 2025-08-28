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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import uuid
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# ================================
# 1. 초기 설정 및 환경 변수 로드
# ================================
load_dotenv() # .env 파일에서 환경 변수 로드

# --- FastAPI 앱 생성 및 CORS 설정 ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 프로덕션에서는 프론트엔드 URL만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Azure Cosmos DB 설정 ---
COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
DATABASE_NAME = "NewsFlowDB"
CONTAINER_NAME = "NewsItems"

# Cosmos DB 클라이언트 초기화
cosmos_client = None
if COSMOS_DB_URI and COSMOS_DB_KEY:
    try:
        cosmos_client = CosmosClient(COSMOS_DB_URI, credential=COSMOS_DB_KEY)
        database = cosmos_client.get_database_client(DATABASE_NAME)
        # 데이터베이스가 없으면 생성
        try:
            database = cosmos_client.create_database_if_not_exists(DATABASE_NAME)
        except exceptions.CosmosResourceExistsError:
            database = cosmos_client.get_database_client(DATABASE_NAME)
        # 컨테이너가 없으면 생성
        try:
            container = database.create_container_if_not_exists(CONTAINER_NAME, partition_key=PartitionKey(path="/category"))
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(CONTAINER_NAME)
        print("Azure Cosmos DB에 성공적으로 연결되었습니다.")
    except Exception as e:
        print(f"[오류] Azure Cosmos DB 연결 실패: {e}")
else:
    print("[경고] Cosmos DB 환경 변수가 설정되지 않았습니다.")

# --- Azure AI 서비스 설정 ---
translator_key = os.getenv("AZURE_TRANSLATOR_KEY")
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"
translator_location = "KoreaCentral"

# --- Azure OpenAI 설정 ---
openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_deployment = "gpt-4o"
openai_key = os.getenv("AZURE_OPENAI_KEY")
openai_api_version = "2025-01-01-preview"

# Azure OpenAI 클라이언트 초기화
openai_client = None
if openai_endpoint and openai_key:
    try:
        openai_client = AzureOpenAI(
            azure_endpoint=openai_endpoint,
            api_key=openai_key,
            api_version=openai_api_version,
        )
        print("Azure OpenAI 서비스에 성공적으로 연결되었습니다.")
    except Exception as e:
        print(f"[오류] Azure OpenAI 연결 실패: {e}")
else:
    print("[경고] Azure OpenAI 환경 변수가 설정되지 않았습니다.")

# ================================
# 2. Pydantic 데이터 모델 정의
# ================================
class TranslatedTitles(BaseModel):
    ko: str
    en: str
    ja: str
    fr: str
    zh_hans: str = Field(..., alias='zh-Hans')

class NewsArticle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    subCategory: str
    link: str
    source: str
    date: str
    summary: str
    reliability: str
    translatedTitles: Dict[str, str]
    imageUrl: Optional[str] = None
    evaluation: str

# ================================
# 3. 핵심 기능 함수 (기존 로직 재사용)
# ================================
def get_original_article_info(google_news_url):
    print(f"  -> [변환 시도] 기존 주소: {google_news_url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    original_url, image_url = google_news_url, None
    try:
        driver.get(google_news_url)
        WebDriverWait(driver, 15).until(lambda d: "news.google.com" not in d.current_url)
        original_url = driver.current_url
        print(f"  -> [변환 완료] 원문 주소: {original_url}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_tag = soup.find('meta', property='og:image')
        if image_tag and image_tag.get('content'):
            image_url = image_tag['content']
            print("  -> 이미지 주소 찾음!")
        else:
            print("  [알림] 이 페이지에는 og:image 태그가 없습니다.")
    except TimeoutException:
        print(f"  [오류] 원문 주소 변환 중 타임아웃 발생. 최종 URL: {driver.current_url}")
        original_url = driver.current_url # 타임아웃 시점의 URL이라도 반환
    except Exception as e:
        print(f"  [오류] 작업 중 오류 발생: {e}")
        original_url = driver.current_url
        print(f"  -> [오류 시점 주소] {original_url}")
    finally:
        driver.quit()
    return {'original_url': original_url, 'image_url': image_url}

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
            body_text = "\n".join([p.get_text(strip=True) for p in article_tag.find_all(['p', 'div']) if p.get_text(strip=True)])
            if len(body_text) > 50:
                print("  -> 본문 수집 성공!")
                return body_text
        print("  [알림] 기사 본문을 찾을 수 없거나 내용이 너무 짧습니다.")
        return None
    except Exception as e:
        print(f"  [오류] 본문 수집 중 오류 발생: {e}")
        return None

def gpt_evaluate(article_text, selected_sources):
    if not openai_client:
        return "GPT 평가 오류: OpenAI 클라이언트가 초기화되지 않았습니다."
    prompt_text = f"""당신은 뉴스 기사의 신뢰도를 평가하는 AI 분석가입니다.
주어진 기사 본문을 바탕으로 다음 두 가지 작업을 수행해주세요.

1. 기사의 핵심 내용을 3~4문장으로 요약해주세요.
2. 기사의 신뢰도를 '높음', '보통', '낮음' 세 단계로 평가하고, 그 이유를 주요 언론사({', '.join(selected_sources)})들의 보도 경향과 비교하여 간략히 서술해주세요.

결과는 다음 형식에 맞춰 한글로만 작성해주세요:
1) [여기에 요약 내용]
신뢰도: [높음/보통/낮음] - [여기에 평가 이유]
"""
    messages = [{"role": "system", "content": "당신은 뉴스 기사의 신뢰도를 평가하고 요약하는 AI 분석가입니다."}, {"role": "user", "content": prompt_text}, {"role": "user", "content": article_text}]
    try:
        completion = openai_client.chat.completions.create(model=openai_deployment, messages=messages, max_tokens=1024)
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 평가 오류: {e}"

def translate_with_azure(text_to_translate, target_languages):
    if not translator_key:
        print("[경고] 번역기 키가 설정되지 않았습니다.")
        return {lang: "Translation Error" for lang in target_languages}
    headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Ocp-Apim-Subscription-Region': translator_location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    params = {'api-version': '3.0', 'from': 'ko', 'to': target_languages}
    body = [{'text': text_to_translate}]
    try:
        response = requests.post(f"{translator_endpoint}/translate", params=params, headers=headers, json=body)
        response.raise_for_status()
        translations = response.json()
        return {t['to']: t['text'] for t in translations[0]['translations']}
    except Exception as e:
        print(f"Azure 번역 API 오류: {e}")
        return {lang: "Translation Error" for lang in target_languages}

# ================================
# 4. API 엔드포인트 정의
# ================================
@app.get("/api/news", response_model=List[NewsArticle])
def get_news(category: Optional[str] = None, limit: int = 50):
    if not container:
        raise HTTPException(status_code=500, detail="Cosmos DB 컨테이너가 초기화되지 않았습니다.")
    query = "SELECT * FROM c ORDER BY c.date DESC OFFSET 0 LIMIT @limit"
    params = [{"name": "@limit", "value": limit}]
    if category and category != 'all':
        query = "SELECT * FROM c WHERE c.category = @category ORDER BY c.date DESC OFFSET 0 LIMIT @limit"
        params.append({"name": "@category", "value": category})
    try:
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=False if category else True))
        return items
    except exceptions.CosmosResourceNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 중 오류 발생: {e}")

@app.post("/api/news/fetch", status_code=202)
def fetch_and_process_news(sub_category: str, main_category: str):
    if not all([container, openai_client, translator_key]):
        raise HTTPException(status_code=500, detail="서비스가 올바르게 초기화되지 않았습니다. 환경 변수를 확인하세요.")
    print(f"[{main_category}] {sub_category} 뉴스 수집 시작...")
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
    feed = feedparser.parse(news_url)
    processed_count = 0
    for entry in feed.entries[:10]: # API 테스트를 위해 개수 제한
        try:
            source = getattr(entry, 'source', {}).get('title', '알 수 없음')
            published_time = entry.get('published_parsed')
            if not published_time: continue
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date < datetime.now() - timedelta(days=30): continue
            print(f"  - '{entry.title[:30]}...' 처리 중")
            article_info = get_original_article_info(entry.link)
            if "news.google.com" in article_info['original_url']: continue # 원문 변환 실패 시 건너뛰기
            body_text = scrape_article_body(article_info['original_url'])
            content_for_gpt = body_text if body_text else entry.summary
            if not content_for_gpt: continue
            evaluation_text = gpt_evaluate(content_for_gpt, ["조선일보", "한겨레"])
            summary_match = re.search(r'1\)(.*?)(?=신뢰도:|\Z)', evaluation_text, re.DOTALL)
            reliability_match = re.search(r'신뢰도:\s*(높음|보통|낮음)', evaluation_text)
            summary = summary_match.group(1).strip() if summary_match else "요약 정보 없음"
            reliability = reliability_match.group(1).strip() if reliability_match else "알 수 없음"
            target_languages = ['en', 'ja', 'fr', 'zh-Hans']
            full_text_to_translate = f"{entry.title}\n{summary}"
            azure_translations = translate_with_azure(full_text_to_translate, target_languages)
            translated_titles = {lang: text.split('\n')[0] for lang, text in azure_translations.items()}
            translated_titles['ko'] = entry.title
            article_id = str(uuid.uuid5(uuid.NAMESPACE_URL, article_info['original_url']))
            news_item = {
                'id': article_id,
                'category': main_category,
                'subCategory': sub_category,
                'link': article_info['original_url'],
                'source': source,
                'date': article_date.isoformat(),
                'summary': summary,
                'reliability': reliability,
                'translatedTitles': translated_titles,
                'imageUrl': article_info['image_url'],
                'evaluation': evaluation_text
            }
            container.upsert_item(body=news_item)
            processed_count += 1
            time.sleep(1)
        except Exception as e:
            print(f"  [오류] 기사 처리 중 오류 발생: {e}")
            continue
    print(f"  -> {processed_count}개 뉴스 처리 및 저장 완료.")
    return {"message": f"{processed_count}개의 뉴스를 성공적으로 처리하고 저장했습니다."}

@app.get("/")
def read_root():
    return {"message": "NewsFlow AI 백엔드 서버입니다. /docs 로 API 문서를 확인하세요."}
