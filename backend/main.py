# ================================
# 0. 라이브러리 임포트
# ================================
import asyncio
import feedparser
import time
import os
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin, urlparse, parse_qs
from openai import AzureOpenAI
import re
import json
import requests
import uuid
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# -------------------------
# Publisher mapping (simple whitelist)
# -------------------------
PUBLISHER_MAP = {
    '파이낸셜뉴스': 'fnnews.com',
    '조선일보': 'chosun.com',
    '연합뉴스': 'yna.co.kr',
    '조선': 'chosun.com',
    '한겨레': 'hani.co.kr',
}

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

# --- ddd 버전의 설정값 추가 ---
user_selected_sources = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]
user_follow_categories = ["정치", "경제", "IT_과학"] # 자동으로 수집할 카테고리
# 테스트용: 로컬 테스트 시에는 아래 라인으로 덮어써서 한 개 카테고리와 소분류만 수집하도록 제한합니다.
# 실제 운영 시에는 이 주석을 지우고 위 설정을 사용하세요.
# user_follow_categories = ["정치"]
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
}

# --- Azure Cosmos DB 설정 ---
COSMOS_DB_URI = os.getenv("COSMOS_DB_URI")
COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
DATABASE_NAME = "NewsFlowDB"
CONTAINER_NAME = "NewsItems"

# Cosmos DB 클라이언트 초기화
container = None
if COSMOS_DB_URI and COSMOS_DB_KEY:
    try:
        cosmos_client = CosmosClient(COSMOS_DB_URI, credential=COSMOS_DB_KEY)
        database = cosmos_client.create_database_if_not_exists(DATABASE_NAME)
        container = database.create_container_if_not_exists(CONTAINER_NAME, partition_key=PartitionKey(path="/category"))
        print("Azure Cosmos DB에 성공적으로 연결되었습니다.")
    except Exception as e:
        print(f"[오류] Azure Cosmos DB 연결 실패: {e}")
else:
    print("[경고] Cosmos DB 환경 변수가 설정되지 않았습니다.")

# --- Azure AI 서비스 설정 ---
translator_key = os.getenv("AZURE_TRANSLATOR_KEY")
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"
translator_location = "KoreaCentral"

# Optional Selenium fallback (disabled by default). Set USE_SELENIUM=true for local debugging if needed.
USE_SELENIUM = os.getenv('USE_SELENIUM', 'false').lower() == 'true'

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
    translatedSummaries: Dict[str, str]
    imageUrl: Optional[str] = None
    evaluation: str

# ================================
# 3. 핵심 기능 함수
# ================================
def get_original_article_info(google_news_url):
    """requests 기반으로 최종 URL과 og:image를 시도합니다. Selenium 의존성을 제거했지만
    동작은 기존과 동일하게 최종 URL을 찾아 반환해야 합니다. 만약 requests로 원문을 찾지 못하면
    입력된 URL을 그대로 반환합니다.
    """
    print(f"  -> [변환 시도] 기존 주소: {google_news_url}")
    image_url = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(google_news_url, headers=headers, timeout=10, allow_redirects=True)
        final_url = resp.url
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Helper: try to fetch candidate page and extract og:image
        def fetch_and_get_og_image(url_candidate):
            try:
                r2 = requests.get(url_candidate, headers=headers, timeout=10, allow_redirects=True)
                s2 = BeautifulSoup(r2.text, 'html.parser')
                og = s2.find('meta', property='og:image') or s2.find('meta', attrs={'name': 'og:image'})
                if og and og.get('content'):
                    return og.get('content')
                # try common image selectors
                img = s2.find('meta', property='twitter:image') or s2.find('link', rel='image_src')
                if img and img.get('content'):
                    return img.get('content')
                if img and img.get('href'):
                    return img.get('href')
                # look for first large <img>
                imgs = s2.find_all('img')
                for im in imgs:
                    src = im.get('src') or im.get('data-src') or im.get('data-original')
                    if src and src.startswith('http') and 'logo' not in src and 'icon' not in src:
                        return src
            except Exception:
                return None
            return None

        # 1) 기본적으로 현재 응답 페이지에서 og:image 추출
        image_tag = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'})
        if image_tag and image_tag.get('content'):
            image_url = image_tag['content']

        # 2) 만약 final_url이 구글 뉴스 페이지이거나 이미지는 구글usercontent(프리뷰)일 경우, 원문 링크 탐색 및 원문에서 이미지 추출 시도
        need_try_original = False
        if 'news.google.com' in final_url:
            need_try_original = True
        if image_url and 'lh3.googleusercontent.com' in image_url:
            need_try_original = True

        if need_try_original:
            # 우선 og:url / canonical을 확인
            meta_url = None
            og_url_tag = soup.find('meta', property='og:url')
            if og_url_tag and og_url_tag.get('content'):
                meta_url = og_url_tag.get('content')
            canon = soup.find('link', rel='canonical')
            if not meta_url and canon and canon.get('href'):
                meta_url = canon.get('href')

            candidate = None
            if meta_url and 'news.google.com' not in meta_url:
                candidate = meta_url
            else:
                # try parsing anchors and url?q patterns
                anchors = soup.find_all('a', href=True)
                for a in anchors:
                    href = a['href']
                    if 'url?q=' in href or '/url?' in href:
                        parsed = urlparse(href)
                        qs = parse_qs(parsed.query)
                        for key in ('q', 'url'):
                            if key in qs and qs[key]:
                                cand = qs[key][0]
                                if cand.startswith('http') and 'news.google.com' not in cand:
                                    candidate = cand
                                    break
                        if candidate:
                            break
                    if href.startswith('http') and 'news.google.com' not in href:
                        candidate = href
                        break
                    if href.startswith('/'):
                        cand = urljoin(final_url, href)
                        if 'news.google.com' not in cand:
                            candidate = cand
                            break

                # additional heuristic: search for attributes that may contain the original URL
                if not candidate:
                    for tag in soup.find_all(True):
                        for attr in ('data-url', 'data-href', 'data-expanded-url', 'data-origin', 'data-amp-url', 'data-src'):
                            val = tag.get(attr)
                            if not val:
                                continue
                            # extract first http(s) URL from attribute
                            m = re.search(r'https?://[^"\'\s>]+', val)
                            if m:
                                cand = m.group(0)
                                if 'news.google.com' not in cand:
                                    candidate = cand
                                    break
                        if candidate:
                            break
                # last resort: search script text for embedded URLs
                if not candidate:
                    scripts = soup.find_all('script')
                    for sc in scripts:
                        txt = sc.string or ''
                        if not txt:
                            continue
                        m = re.search(r'https?://[^"\'\s>]+', txt)
                        if m:
                            cand = m.group(0)
                            if 'news.google.com' not in cand:
                                candidate = cand
                                break

            # if candidate found, try to fetch its og:image
            if candidate:
                fetched_img = fetch_and_get_og_image(candidate)
                if fetched_img:
                    image_url = fetched_img
                    final_url = candidate
                else:
                    # try amp link
                    amp = soup.find('link', rel='amphtml')
                    if amp and amp.get('href'):
                        amp_candidate = amp.get('href')
                        fetched_img = fetch_and_get_og_image(amp_candidate)
                        if fetched_img:
                            image_url = fetched_img
                            final_url = amp_candidate
        # 마지막 시도: 만약 image_url 없음이면 entry-level media may exist; caller handles none
        if image_url:
            print("  -> 이미지 주소 찾음 (requests)!")
        return {'original_url': final_url, 'image_url': image_url}
    except Exception as e:
        print(f"  [오류] requests로 원문 변환 중 오류 발생: {e}")
        return {'original_url': google_news_url, 'image_url': None}


def extract_original_from_entry(entry):
    """Try various RSS entry fields to extract the original article URL.
    Returns a URL string or None.
    """
    try:
        # 1) entry.id or guid
        eid = getattr(entry, 'id', None) or getattr(entry, 'guid', None)
        if eid and isinstance(eid, str):
            m = re.search(r"https?://[^\s\"']+", eid)
            if m:
                url = m.group(0)
                if 'news.google.com' not in url:
                    print(f"  -> [RSS:id] extracted: {url}")
                    return url

        # 2) links array (common case)
        links = getattr(entry, 'links', None)
        if links:
            for l in links:
                href = l.get('href') or l.get('link')
                rel = l.get('rel', '')
                ltype = l.get('type', '')
                if href and href.startswith('http') and 'news.google.com' not in href:
                    # prefer alternate/text/html
                    if 'alternate' in rel or 'html' in ltype or True:
                        print(f"  -> [RSS:links] candidate: {href}")
                        return href

        # 3) summary HTML anchor
        summary = getattr(entry, 'summary', None) or getattr(entry, 'summary_detail', None)
        if summary:
            val = summary if isinstance(summary, str) else (getattr(summary, 'value', '') or '')
            soup = BeautifulSoup(val, 'html.parser')
            a = soup.find('a', href=True)
            if a:
                href = a['href']
                if href.startswith('/'):
                    href = urljoin(getattr(entry, 'link', ''), href)
                if href and href.startswith('http') and 'news.google.com' not in href:
                    print(f"  -> [RSS:summary] anchor: {href}")
                    return href

        # 4) entry.link query params (e.g., /url?q=)
        link = getattr(entry, 'link', None)
        if link and isinstance(link, str):
            parsed = urlparse(link)
            qs = parse_qs(parsed.query)
            for key in ('q', 'url'):
                if key in qs and qs[key]:
                    cand = qs[key][0]
                    if cand.startswith('http') and 'news.google.com' not in cand:
                        print(f"  -> [RSS:link-q] found: {cand}")
                        return cand

        # 5) media:content / media_thumbnail fields sometimes contain original image URL only
        # not used here as original link, skip
    except Exception as e:
        print(f"  [WARN] extract_original_from_entry error: {e}")
    return None


def call_external_og_api(url):
    """폴백: 외부 OG 미리보기 API 호출. API키가 없으면 None 반환."""
    try:
        # Microlink 기본 REST 호출: https://api.microlink.io?url={URL}
        api_url = "https://api.microlink.io/"
        params = {'url': url}
        headers = {'User-Agent': 'NewsFlowAI/1.0'}
        r = requests.get(api_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        img = None
        # Microlink 응답 구조에 따라 안전하게 파싱
        root = data.get('data') if isinstance(data, dict) else data
        if not root:
            root = data

        if isinstance(root, dict):
            # 1) root.image.url
            image_block = root.get('image')
            if isinstance(image_block, dict):
                img = image_block.get('url') or image_block.get('src')
            # 2) root.meta.image
            if not img:
                meta = root.get('meta') or {}
                if isinstance(meta, dict):
                    img = meta.get('image') or meta.get('og:image')
            # 3) root.thumbnail or root.screenshot
            if not img:
                img = root.get('thumbnail') or root.get('screenshot')

        if img:
            print(f"[IMAGE] Microlink 성공 -> {img}")
            return img
        else:
            print(f"[WARN] Microlink 호출 성공했지만 이미지 미발견, status: {data.get('status') if isinstance(data, dict) else 'unknown'}")
            return None
    except Exception as e:
        print(f"[WARN] Microlink 호출 실패: {e}")
        return None


def extract_image_hybrid(article_data):
    """하이브리드 폴백 전략으로 이미지 URL 추출.
    article_data: dict-like with keys: 'link', 'source', 'media_thumbnail', 'media_content', 'summary'
    """
    link = article_data.get('link')
    source = article_data.get('source')

    # 1단계: RSS 피드 레벨(media_thumbnail/media_content)
    try:
        # media_thumbnail
        mt = article_data.get('media_thumbnail') or article_data.get('media:thumbnail')
        if mt:
            if isinstance(mt, list) and mt:
                cand = mt[0].get('url') if isinstance(mt[0], dict) else mt[0]
                if cand:
                    print(f"[IMAGE] 단계1: media_thumbnail 성공 -> {cand}")
                    return cand
            elif isinstance(mt, dict):
                cand = mt.get('url')
                if cand:
                    print(f"[IMAGE] 단계1: media_thumbnail dict 성공 -> {cand}")
                    return cand
        # media_content
        mc = article_data.get('media_content') or article_data.get('media:content')
        if mc:
            if isinstance(mc, list) and mc:
                cand = mc[0].get('url') if isinstance(mc[0], dict) else mc[0]
                if cand:
                    print(f"[IMAGE] 단계1: media_content 성공 -> {cand}")
                    return cand
            elif isinstance(mc, dict):
                cand = mc.get('url')
                if cand:
                    print(f"[IMAGE] 단계1: media_content dict 성공 -> {cand}")
                    return cand
    except Exception as e:
        print(f"[WARN] 단계1 오류: {e}")

    # helper: parse srcset and return largest url
    def parse_srcset_get_largest(srcset):
        try:
            parts = [p.strip() for p in srcset.split(',') if p.strip()]
            best_url = None
            best_w = 0
            for p in parts:
                segs = p.split()
                url = segs[0]
                w = 0
                if len(segs) > 1 and segs[1].endswith('w'):
                    try:
                        w = int(segs[1][:-1])
                    except Exception:
                        w = 0
                if w > best_w:
                    best_w = w
                    best_url = url
            return best_url
        except Exception:
            return None

    # 2/3단계(퍼블리셔 매핑, 페이지 파싱)를 제거하고 Microlink로 직접 폴백합니다.
    # Microlink는 페이지를 분석하여 메타/스크린샷 등의 이미지를 제공하므로
    # 여기서는 feed 레벨(media_*) 이후 Microlink 호출만 수행합니다.
    try:
        if link:
            ext = call_external_og_api(link)
            if ext:
                print(f"[IMAGE] Microlink 폴백 성공 -> {ext}")
                return ext
    except Exception as e:
        print(f"[WARN] Microlink 폴백 실패: {e}")

    # 4단계: 외부 OG 미리보기 API 폴백
    try:
        if link:
            ext = call_external_og_api(link)
            if ext:
                print(f"[IMAGE] 단계4: 외부 OG API 성공 -> {ext}")
                return ext
    except Exception as e:
        print(f"[WARN] 단계4 오류: {e}")

    print("[IMAGE] 모든 단계 실패: 이미지 없음")
    return None

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
                return body_text
        return None
    except Exception as e:
        print(f"  [오류] 본문 수집 중 오류 발생: {e}")
        return None

def gpt_evaluate(article_text, selected_sources):
    """GPT에 기사 텍스트를 보내 요약(summary)과 신뢰도(reliability)를 JSON으로 반환하도록 요청합니다.
    반환값: 성공 시 dict {"summary": str, "reliability": str, "raw": str}, 실패 시 에러 문자열.
    """
    if not openai_client:
        return "GPT 평가 오류: OpenAI 클라이언트가 초기화되지 않았습니다."

    # 명확한 JSON 포맷을 요구하는 프롬프트
    prompt_text = (
        "기사 본문을 아래 요구사항에 맞추어 응답해 주세요.\n"
        "요구사항: 1) 한국어로 요약(summary)를 3문장 이내로 작성.\n"
        "2) 신뢰도(reliability)는 '높음'|'보통'|'낮음' 중 하나로 평가.\n"
        "3) 추가 설명(explanation)은 선택적으로 포함 가능.\n"
        "응답 형식: 반드시 유효한 JSON 객체만 반환하세요. 예: {\"summary\": \"요약문\", \"reliability\": \"보통\", \"explanation\": \"설명\"}\n"
        "본문(아래)에 기반해 응답해 주세요:\n"
    )

    messages = [
        {"role": "system", "content": "뉴스 기사 요약 및 신뢰도 평가를 JSON으로만 응답하세요."},
        {"role": "user", "content": prompt_text},
        {"role": "user", "content": article_text}
    ]

    try:
        completion = openai_client.chat.completions.create(model=openai_deployment, messages=messages, max_tokens=1024)
        raw_text = completion.choices[0].message.content.strip()
        # 모델이 추가 텍스트를 붙여 보내는 경우 JSON 객체만 추출해 파싱 시도
        json_match = re.search(r'(\{[\s\S]*\})', raw_text)
        if json_match:
            json_str = json_match.group(1)
            try:
                parsed = json.loads(json_str)
                # 보장: summary, reliability 키가 존재하도록 기본값 적용
                summary = parsed.get('summary', '').strip() if isinstance(parsed.get('summary', ''), str) else ''
                reliability = parsed.get('reliability', '').strip() if isinstance(parsed.get('reliability', ''), str) else ''
                return {'summary': summary or '요약 정보 없음', 'reliability': reliability or '알 수 없음', 'raw': raw_text}
            except Exception as e:
                # JSON 파싱 실패 시 폴백
                return {'summary': '', 'reliability': '', 'raw': raw_text}
        else:
            # JSON 형태를 찾지 못하면 전체 텍스트를 raw로 반환
            return {'summary': '', 'reliability': '', 'raw': raw_text}
    except Exception as e:
        return f"GPT 평가 오류: {e}"

def translate_with_azure(text_to_translate, target_languages):
    if not translator_key: return {lang: "Translation Error" for lang in target_languages}
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
        return {lang: "Translation Error" for lang in target_languages}

# ================================
# 4. 뉴스 처리 및 저장 로직
# ================================
async def process_and_save_news(main_category: str, sub_category: str):
    if not all([container, openai_client, translator_key]):
        print("[오류] 서비스가 올바르게 초기화되지 않아 뉴스 처리를 건너뜁니다.")
        return

    print(f"[{main_category}] '{sub_category}' 뉴스 수집 시작...")
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
    feed = feedparser.parse(news_url)
    debug = os.getenv('DEBUG_NEWS', 'false').lower() == 'true'

    print(f"[INFO] RSS feed URL: {news_url}")
    print(f"[INFO] feed.entries count: {len(feed.entries)}")
    for i, e in enumerate(feed.entries[:5]):
        try:
            title = getattr(e, 'title', '')
            link = getattr(e, 'link', '')
            print(f"[INFO] entry[{i}] title: {title[:80]} link: {link}")
        except Exception:
            pass

    if debug:
        print(f"[DEBUG] DEBUG_NEWS mode enabled")

    processed_count = 0

    try:
        for entry in feed.entries[:5]:
            try:
                # Early original URL resolution for logging and to avoid later Google-preview images
                original = None
                links = getattr(entry, 'links', None)
                if links:
                    for l in links:
                        href = l.get('href') or l.get('link')
                        if href and href.startswith('http') and 'news.google.com' not in href:
                            original = href
                            break
                if not original and getattr(entry, 'summary', None):
                    soup_summary = BeautifulSoup(entry.summary, 'html.parser')
                    a_tag = soup_summary.find('a', href=True)
                    if a_tag and a_tag['href']:
                        href = a_tag['href']
                        if href.startswith('/'):
                            href = urljoin(getattr(entry, 'link', ''), href)
                        original = href
                # if still not found, try quick requests-based resolution (may perform one request)
                if not original:
                    try:
                        tmp_info = get_original_article_info(getattr(entry, 'link', ''))
                        original = tmp_info.get('original_url')
                    except Exception:
                        original = None

                print(f"[DEBUG] 사전 원문 변환 결과: {original}")

                source = getattr(entry, 'source', {}).get('title', '알 수 없음')
                published_time = entry.get('published_parsed')

                if debug:
                    print(f"[DEBUG] Processing entry: {getattr(entry, 'title', '')[:80]}")
                    print(f"[DEBUG] entry.link: {getattr(entry, 'link', '')}")
                    print(f"[DEBUG] source: {source}")
                    print(f"[DEBUG] published_parsed present: {bool(published_time)}")

                if not published_time:
                    if debug:
                        print("[DEBUG] Skipping: no published_parsed")
                    continue

                article_date = datetime.fromtimestamp(time.mktime(published_time))
                if article_date < datetime.now() - timedelta(days=30):
                    if debug:
                        print("[DEBUG] Skipping: older than 30 days")
                    continue

                # Try extracting original URL from RSS entry first
                original = extract_original_from_entry(entry)
                if original:
                    article_info = {'original_url': original, 'image_url': None}
                    if debug:
                        print(f"[DEBUG] original extracted from entry: {original}")
                else:
                    article_info = get_original_article_info(getattr(entry, 'link', ''))
                    if debug:
                        print(f"[DEBUG] resolved original via requests: {article_info.get('original_url')}")

                # Hybrid image extraction
                if not article_info.get('image_url'):
                    hybrid_img = extract_image_hybrid({
                        'link': article_info.get('original_url') or getattr(entry, 'link', ''),
                        'source': source,
                        'media_thumbnail': getattr(entry, 'media_thumbnail', None),
                        'media_content': getattr(entry, 'media_content', None),
                        'summary': getattr(entry, 'summary', None)
                    })
                    if hybrid_img:
                        article_info['image_url'] = hybrid_img
                        if debug:
                            print(f"[DEBUG] hybrid image extraction succeeded: {hybrid_img}")

                # Get content for GPT
                body_text = None
                if article_info.get('original_url') and 'news.google.com' not in article_info.get('original_url'):
                    body_text = scrape_article_body(article_info['original_url'])
                content_for_gpt = body_text if body_text else getattr(entry, 'summary', None)
                if not content_for_gpt:
                    if debug:
                        print("[DEBUG] Skipping: no content_for_gpt")
                    continue

                gpt_result = gpt_evaluate(content_for_gpt, user_selected_sources)
                summary = '요약 정보 없음'
                reliability = '알 수 없음'
                evaluation_text = ''
                if isinstance(gpt_result, dict):
                    evaluation_text = gpt_result.get('raw', '')
                    summary = gpt_result.get('summary') or summary
                    reliability = gpt_result.get('reliability') or reliability
                else:
                    evaluation_text = str(gpt_result)

                # Translations
                target_languages = ['en', 'ja', 'fr', 'zh-Hans']
                azure_title_translations = translate_with_azure(getattr(entry, 'title', ''), target_languages)
                translated_titles = {lang: text for lang, text in azure_title_translations.items()}
                translated_titles['ko'] = getattr(entry, 'title', '')
                azure_summary_translations = translate_with_azure(summary, target_languages)
                translated_summaries = {lang: text for lang, text in azure_summary_translations.items()}
                translated_summaries['ko'] = summary

                article_id = str(uuid.uuid5(uuid.NAMESPACE_URL, article_info.get('original_url') or getattr(entry, 'link', '')))
                news_item = {
                    'id': article_id,
                    'category': main_category,
                    'subCategory': sub_category,
                    'link': article_info.get('original_url') or getattr(entry, 'link', ''),
                    'source': source,
                    'date': article_date.isoformat(),
                    'summary': summary,
                    'reliability': reliability,
                    'translatedTitles': translated_titles,
                    'translatedSummaries': translated_summaries,
                    'imageUrl': article_info.get('image_url'),
                    'evaluation': evaluation_text
                }

                if debug:
                    try:
                        print("[DEBUG] Upserting news_item:\n" + json.dumps(news_item, ensure_ascii=False, indent=2))
                    except Exception:
                        print("[DEBUG] Upserting news_item (could not serialize to JSON)")

                try:
                    resp = container.upsert_item(body=news_item)
                    if debug:
                        try:
                            print("[DEBUG] Upsert response:\n" + json.dumps(resp, ensure_ascii=False, indent=2))
                        except Exception:
                            print("[DEBUG] Upsert response (non-serializable)")
                    try:
                        read_back = container.read_item(item=article_id, partition_key=news_item.get('category'))
                        if debug:
                            print(f"[DEBUG] Read back item id: {read_back.get('id')}")
                    except Exception as e:
                        if debug:
                            print(f"[DEBUG] Read back failed: {e}")
                except Exception as e:
                    print(f"[ERROR] Upsert failed: {e}")

                processed_count += 1
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                print(f"[취소] 기사 처리 작업이 취소되었습니다. 카테고리={main_category}, 소분류={sub_category}")
                raise
            except Exception as e:
                print(f"  [오류] 기사 처리 중 오류 발생: {e}")
                continue

    except asyncio.CancelledError:
        print(f"[취소] 뉴스 처리 작업이 취소되었습니다. 카테고리={main_category}, 소분류={sub_category}")
        return
    except Exception as e:
        print(f"[오류] process_and_save_news 루프 중 오류: {e}")

    print(f"  -> [{main_category}] '{sub_category}' 카테고리에서 {processed_count}개 뉴스 처리 완료.")


async def process_and_save_news_v2(main_category: str, sub_category: str):
    """Clean implementation (v2) that uses the hybrid image extractor and preserves existing behavior.
    This function will be used instead of the older process_and_save_news to avoid indentation issues.
    """
    if not all([container, openai_client, translator_key]):
        print("[오류] 서비스가 올바르게 초기화되지 않아 뉴스 처리를 건너뜁니다.")
        return

    print(f"[{main_category}] '{sub_category}' 뉴스 수집 시작...")
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
    feed = feedparser.parse(news_url)
    debug = os.getenv('DEBUG_NEWS', 'false').lower() == 'true'

    print(f"[INFO] RSS feed URL: {news_url}")
    print(f"[INFO] feed.entries count: {len(feed.entries)}")

    processed_count = 0

    for entry in feed.entries[:5]:
        try:
            # Early original URL resolution for logging and to avoid later Google-preview images
            original = None
            links = getattr(entry, 'links', None)
            if links:
                for l in links:
                    href = l.get('href') or l.get('link')
                    if href and href.startswith('http') and 'news.google.com' not in href:
                        original = href
                        break
            if not original and getattr(entry, 'summary', None):
                soup_summary = BeautifulSoup(entry.summary, 'html.parser')
                a_tag = soup_summary.find('a', href=True)
                if a_tag and a_tag['href']:
                    href = a_tag['href']
                    if href.startswith('/'):
                        href = urljoin(getattr(entry, 'link', ''), href)
                    original = href
            # if still not found, try quick requests-based resolution (may perform one request)
            if not original:
                try:
                    tmp_info = get_original_article_info(getattr(entry, 'link', ''))
                    original = tmp_info.get('original_url')
                except Exception:
                    original = None

            print(f"[DEBUG] 사전 원문 변환 결과: {original}")

            source = getattr(entry, 'source', {}).get('title', '알 수 없음')
            published_time = entry.get('published_parsed')
            if debug:
                print(f"[DEBUG] Processing entry: {getattr(entry, 'title', '')[:80]}")
                print(f"[DEBUG] entry.link: {getattr(entry, 'link', '')}")
                print(f"[DEBUG] source: {source}")
                print(f"[DEBUG] published_parsed present: {bool(published_time)}")
            if not published_time:
                if debug: print("[DEBUG] Skipping: no published_parsed")
                continue
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date < datetime.now() - timedelta(days=30):
                if debug: print("[DEBUG] Skipping: older than 30 days")
                continue

            # resolve original url
            original = None
            links = getattr(entry, 'links', None)
            if links:
                for l in links:
                    href = l.get('href') or l.get('link')
                    if href and href.startswith('http') and 'news.google.com' not in href:
                        original = href
                        break
            if not original and getattr(entry, 'summary', None):
                soup_summary = BeautifulSoup(entry.summary, 'html.parser')
                a_tag = soup_summary.find('a', href=True)
                if a_tag and a_tag['href']:
                    href = a_tag['href']
                    if href.startswith('/'):
                        href = urljoin(getattr(entry, 'link', ''), href)
                    original = href

            if not original:
                article_info = get_original_article_info(getattr(entry, 'link', ''))
                # print resolved original for immediate visibility
                print(f"[DEBUG] 사전 원문 변환 결과(v2): {article_info.get('original_url')}")
            else:
                article_info = {'original_url': original, 'image_url': None}
                print(f"[DEBUG] 사전 원문 변환 결과(v2): {original}")

            # hybrid image extraction if needed
            if not article_info.get('image_url'):
                hybrid_img = extract_image_hybrid({
                    'link': article_info.get('original_url') or getattr(entry, 'link', ''),
                    'source': source,
                    'media_thumbnail': getattr(entry, 'media_thumbnail', None),
                    'media_content': getattr(entry, 'media_content', None),
                    'summary': getattr(entry, 'summary', None)
                })
                if hybrid_img:
                    article_info['image_url'] = hybrid_img
                    if debug:
                        print(f"[DEBUG] hybrid image extraction succeeded: {hybrid_img}")

            # ensure we have content for GPT
            body_text = None
            if article_info.get('original_url') and 'news.google.com' not in article_info.get('original_url'):
                body_text = scrape_article_body(article_info['original_url'])
            content_for_gpt = body_text if body_text else getattr(entry, 'summary', None)
            if not content_for_gpt:
                if debug:
                    print("[DEBUG] Skipping: no content_for_gpt")
                continue

            gpt_result = gpt_evaluate(content_for_gpt, user_selected_sources)
            summary = '요약 정보 없음'
            reliability = '알 수 없음'
            evaluation_text = ''
            if isinstance(gpt_result, dict):
                evaluation_text = gpt_result.get('raw', '')
                summary = gpt_result.get('summary') or summary
                reliability = gpt_result.get('reliability') or reliability
            else:
                evaluation_text = str(gpt_result)

            # translations
            target_languages = ['en', 'ja', 'fr', 'zh-Hans']
            azure_title_translations = translate_with_azure(getattr(entry, 'title', ''), target_languages)
            translated_titles = {lang: text for lang, text in azure_title_translations.items()}
            translated_titles['ko'] = getattr(entry, 'title', '')
            azure_summary_translations = translate_with_azure(summary, target_languages)
            translated_summaries = {lang: text for lang, text in azure_summary_translations.items()}
            translated_summaries['ko'] = summary

            article_id = str(uuid.uuid5(uuid.NAMESPACE_URL, article_info.get('original_url') or getattr(entry, 'link', '')))
            news_item = {
                'id': article_id,
                'category': main_category,
                'subCategory': sub_category,
                'link': article_info.get('original_url') or getattr(entry, 'link', ''),
                'source': source,
                'date': article_date.isoformat(),
                'summary': summary,
                'reliability': reliability,
                'translatedTitles': translated_titles,
                'translatedSummaries': translated_summaries,
                'imageUrl': article_info.get('image_url'),
                'evaluation': evaluation_text
            }

            if debug:
                try:
                    print("[DEBUG] Upserting news_item:\n" + json.dumps(news_item, ensure_ascii=False, indent=2))
                except Exception:
                    print("[DEBUG] Upserting news_item (could not serialize to JSON)")

            try:
                resp = container.upsert_item(body=news_item)
                if debug:
                    try:
                        print("[DEBUG] Upsert response:\n" + json.dumps(resp, ensure_ascii=False, indent=2))
                    except Exception:
                        print("[DEBUG] Upsert response (non-serializable)")
                try:
                    read_back = container.read_item(item=article_id, partition_key=news_item.get('category'))
                    if debug:
                        print(f"[DEBUG] Read back item id: {read_back.get('id')}")
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Read back failed: {e}")
            except Exception as e:
                print(f"[ERROR] Upsert failed: {e}")

            processed_count += 1
            await asyncio.sleep(1)

        except asyncio.CancelledError:
            print(f"[취소] 기사 처리 작업이 취소되었습니다. 카테고리={main_category}, 소분류={sub_category}")
            raise
        except Exception as e:
            print(f"  [오류] 기사 처리 중 오류 발생: {e}")
            continue

    print(f"  -> [{main_category}] '{sub_category}' 카테고리에서 {processed_count}개 뉴스 처리 완료.")

# ================================
# 5. 백그라운드 및 시작 이벤트
# ================================
async def fetch_all_categories_in_background():
    print("🚀 서버 시작 - 백그라운드 뉴스 수집을 시작합니다.")


    # 모든 카테고리와 소분류를 순회하여 처리합니다.
    # 로컬 테스트 목적의 제한은 제거되었습니다.
    for main_category, sub_categories in categories.items():
        for sub_category in sub_categories:
            await process_and_save_news_v2(main_category, sub_category)
    print("✅ 모든 카테고리의 뉴스 수집 및 처리가 완료되었습니다.")

@app.on_event("startup")
async def startup_event():
    print("서버 시작: 백그라운드 뉴스 수집 작업을 예약합니다.")
    # use new v2 processor
    asyncio.create_task(fetch_all_categories_in_background())

# ================================
# 6. API 엔드포인트 정의
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
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=False if category and category != 'all' else True))
        return items
    except exceptions.CosmosResourceNotFoundError:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 중 오류 발생: {e}")


@app.get("/api/original")
def api_get_original(url: str):
    """주어진 Google News RSS/article URL에서 원문(original_url)과 추출된 이미지(image_url)를 반환합니다.
    사용법: GET /api/original?url={GOOGLE_NEWS_URL}
    """
    if not url:
        raise HTTPException(status_code=400, detail="url 쿼리 파라미터가 필요합니다.")
    try:
        result = get_original_article_info(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"원문 추출 중 오류: {e}")


@app.post("/api/news/sample")
def insert_sample_news():
    """샘플 뉴스 항목을 생성하여 Cosmos에 업서트합니다. (로컬 테스트 용)"""
    if not container:
        raise HTTPException(status_code=500, detail="Cosmos DB 컨테이너가 초기화되지 않았습니다.")
    try:
        sample_id = str(uuid.uuid4())
        sample_item = {
            'id': sample_id,
            'category': '테스트',
            'subCategory': '샘플',
            'link': 'https://example.com/sample-article',
            'source': '샘플언론사',
            'date': datetime.now().isoformat(),
            'summary': '이것은 샘플 요약입니다.',
            'reliability': '보통',
            'translatedTitles': {'ko': '샘플 제목', 'en': 'Sample Title', 'ja': 'サンプル', 'fr': 'Exemple', 'zh-Hans': '示例'},
            'translatedSummaries': {'ko': '이것은 샘플 요약입니다.', 'en': 'This is a sample summary.', 'ja': 'これはサンプルの要約です。', 'fr': 'Ceci est un résumé exemple.', 'zh-Hans': '这是一个示例摘要。'},
            'imageUrl': None,
            'evaluation': '샘플 GPT 평가 텍스트'
        }
        container.upsert_item(body=sample_item)
        return {"status": "ok", "id": sample_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"샘플 삽입 중 오류: {e}")

@app.get("/")
def read_root():
    return {"message": "NewsFlow AI 백엔드 서버입니다. /docs 로 API 문서를 확인하세요."}