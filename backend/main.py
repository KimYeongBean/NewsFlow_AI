import os
import time
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from openai import AzureOpenAI
import re
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- FastAPI 앱 초기화 ---
app = FastAPI()

# CORS 미들웨어 설정 (프론트엔드 개발 서버 주소 명시적 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Azure OpenAI 클라이언트 초기화 ---
try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://newscheck2.openai.azure.com/"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY", "Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53"),
        api_version="2025-01-01-preview",
    )
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-nano")
except Exception as e:
    print(f"환경변수 또는 Azure OpenAI 초기화 오류: {e}")
    client = None

# --- 데이터 모델 정의 (Pydantic) ---
class NewsRequest(BaseModel):
    categories: List[str] = Field(..., example=["정치", "경제"], description="분석을 원하는 뉴스 대분류 카테고리 리스트")
    trusted_sources: List[str] = Field(..., example=["조선일보", "한겨레"], description="신뢰도 평가의 기준이 될 언론사 리스트")

class Article(BaseModel):
    title: str
    link: str
    source: str
    date: str
    summary: str
    reliability: str
    reliability_class: str

class NewsResponse(BaseModel):
    category: str
    sub_category: str
    articles: List[Article]

# --- 뉴스 관련 상수 및 헬퍼 함수 ---
ALL_SOURCES = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제'
]
CATEGORIES = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계']
}
MAX_ARTICLES_PER_SUB_CATEGORY = 5 # 데모를 위해 기사 수를 줄임
ONE_MONTH_AGO = datetime.now() - timedelta(days=30)

def fetch_news_from_google(sub_category: str):
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
    feed = feedparser.parse(news_url)
    
    articles = []
    for entry in feed.entries:
        if len(articles) >= MAX_ARTICLES_PER_SUB_CATEGORY:
            break
        
        source_name = getattr(entry, 'source', {}).get('title')
        if source_name and source_name in ALL_SOURCES:
            published_time = entry.get('published_parsed')
            if not published_time:
                continue
            
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date >= ONE_MONTH_AGO:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source_name,
                    'date': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': entry.title # 평가를 위해 제목을 content로 사용
                })
    return articles

def gpt_evaluate(article_text: str, selected_sources: List[str]):
    if not client:
        return "GPT 클라이언트가 초기화되지 않았습니다.", "오류", "error"

    prompt_text = f"""
    당신은 뉴스 요약 및 신뢰도 분석 전문가입니다.
    사용자가 신뢰하는 언론사 목록: {', '.join(selected_sources)}

    아래 뉴스 제목을 기반으로 다음 항목을 분석하세요:
    1. 한 문장으로 핵심 내용 요약
    2. 신뢰도 등급 (높음, 보통, 낮음)

    신뢰도 평가 기준:
    - '높음': 사용자가 신뢰하는 언론사 또는 주요 언론사(예: 조선, 중앙, 한겨레 등)의 사실 기반 보도.
    - '보통': 제목만으로 판단하기 어렵거나, 연예/가십 등 중립적인 정보.
    - '낮음': 근거가 부족하거나, 지나치게 선정적이거나, 출처가 불분명한 경우.

    결과는 다음 형식으로만 출력해야 합니다. 다른 설명은 절대 추가하지 마세요.
    요약: [여기에 한 문장 요약]
    신뢰도: [높음/보통/낮음]
    """
    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": article_text}
    ]

    try:
        completion = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_completion_tokens=200, # 파라미터 이름 수정
            temperature=1
        )
        result_text = completion.choices[0].message.content.strip()
        
        summary_match = re.search(r"요약:\s*(.*)", result_text)
        reliability_match = re.search(r"신뢰도:\s*(높음|보통|낮음)", result_text)
        
        summary = summary_match.group(1).strip() if summary_match else "요약 정보를 추출할 수 없습니다."
        reliability = reliability_match.group(1).strip() if reliability_match else "알 수 없음"
        
        if "높음" in reliability:
            reliability_class = "high"
        elif "보통" in reliability:
            reliability_class = "medium"
        else:
            reliability_class = "low"
            
        return summary, reliability, reliability_class

    except Exception as e:
        print(f"GPT 평가 중 오류 발생: {e}")
        return f"GPT 평가 오류: {e}", "오류", "error"


# --- API 엔드포인트 정의 ---
@app.get("/")
def read_root():
    return {"message": "NewsFlow AI 분석 서버에 오신 것을 환영합니다."}

@app.post("/api/analyze", response_model=List[NewsResponse])
async def analyze_news(request: NewsRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Azure OpenAI 서비스가 설정되지 않았습니다. 환경변수를 확인하세요.")

    response_data = []
    
    user_main_categories = request.categories
    
    for main_cat in user_main_categories:
        if main_cat not in CATEGORIES:
            continue
            
        for sub_cat in CATEGORIES[main_cat]:
            print(f"처리 중: [{main_cat}] > [{sub_cat}]")
            
            try:
                fetched_articles = fetch_news_from_google(sub_cat)
                analyzed_articles = []
                
                for article_data in fetched_articles:
                    summary, reliability, reliability_class = gpt_evaluate(article_data['content'], request.trusted_sources)
                    
                    analyzed_articles.append(Article(
                        title=article_data['title'],
                        link=article_data['link'],
                        source=article_data['source'],
                        date=article_data['date'],
                        summary=summary,
                        reliability=reliability,
                        reliability_class=reliability_class
                    ))
                    time.sleep(0.5) # API 호출 속도 조절

                if analyzed_articles:
                    response_data.append(NewsResponse(
                        category=main_cat,
                        sub_category=sub_cat,
                        articles=analyzed_articles
                    ))
            except Exception as e:
                print(f"카테고리 [{sub_cat}] 처리 중 오류: {e}")
                # 특정 서브카테고리에서 오류가 발생해도 계속 진행
                continue
                
    if not response_data:
        raise HTTPException(status_code=404, detail="요청된 카테고리에서 뉴스를 찾을 수 없거나 처리 중 오류가 발생했습니다.")
        
    return response_data

# 로컬 개발 환경에서 uvicorn으로 직접 실행하기 위한 코드
if __name__ == "__main__":
    import uvicorn
    print("로컬 개발 서버를 시작합니다. http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
