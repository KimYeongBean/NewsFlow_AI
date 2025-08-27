# ================================
# 0. 라이브러리 불러오기
# ================================
# FastAPI 관련 라이브러리
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict

# 기존 뉴스 분석 관련 라이브러리
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from openai import AsyncAzureOpenAI # 💡 비동기 처리를 위해 AsyncAzureOpenAI를 사용합니다.
import re
import asyncio # 💡 여러 작업을 동시에 실행하기 위한 비동기 라이브러리

# ================================
# 1. FastAPI 앱 초기화 및 기본 설정
# ================================
# FastAPI 애플리케이션 객체를 생성합니다. 이 객체가 API 서버의 중심이 됩니다.
app = FastAPI(
    title="뉴스 분석 API (News Analyzer API)",
    description="선택한 언론사와 카테고리를 기반으로 뉴스를 수집하고 AI로 요약 및 신뢰도를 평가하는 API입니다.",
    version="1.0.0"
)

# 사용자가 선택할 수 있는 전체 언론사 목록입니다.
all_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제', '매일경제', '프레시안', '머니투데이'
]

# 사용자가 선택할 수 있는 뉴스 카테고리 목록입니다.
categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계']
}

MAX_ARTICLES_PER_CATEGORY = 10 # 💡 테스트를 위해 최대 기사 수를 10개로 줄입니다. 필요시 늘리세요.
one_month_ago = datetime.now() - timedelta(days=30)

# ================================
# 2. Azure OpenAI 비동기 클라이언트 초기화
# ================================
async_client = AsyncAzureOpenAI(
    azure_endpoint="https://newscheck2.openai.azure.com/",
    api_key="Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53",
    api_version="2025-01-01-preview",
)

# ================================
# 3. API 데이터 모델 정의 (Pydantic)
# ================================
# API 요청 시 body에 포함될 데이터의 형식을 정의합니다.
class AnalysisRequest(BaseModel):
    selected_sources: List[str] = Field(..., description="분석 기준으로 삼을 언론사 5개의 목록", min_length=5, max_length=5)
    selected_categories: List[str] = Field(..., description="수집을 원하는 뉴스 카테고리 목록 (최소 1개 이상)", min_length=1)

# API 응답 시 반환될 데이터의 형식을 정의합니다.
class EvaluatedArticle(BaseModel):
    title: str
    link: str
    source: str
    date: str
    summary: str
    reliability_grade: str
    reliability_reason: str

# ================================
# 4. 핵심 로직 함수 (기존 코드 재사용 및 수정)
# ================================
# 뉴스 수집 함수는 기존과 거의 동일합니다.
def fetch_news(sub_category: str) -> List[Dict]:
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(news_url)
    articles = []
    for entry in feed.entries:
        if len(articles) >= MAX_ARTICLES_PER_CATEGORY: break
        source_name = getattr(entry, 'source', None)
        if source_name and source_name.title in all_sources:
            published_time = entry.get('published_parsed')
            if not published_time: continue
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date < one_month_ago: continue
            content = re.sub('<[^<]+?>', '', entry.summary if hasattr(entry, 'summary') else entry.title)
            articles.append({
                'title': entry.title, 'link': entry.link, 'source': source_name.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'), 'content': content
            })
    return articles

# 💡 GPT 평가 함수를 비동기(async) 함수로 변경합니다.
async def gpt_evaluate_async(article: Dict) -> Dict:
    prompt_text = f"""
[분석할 뉴스 기사]
- 제목: {article['title']}
- 내용: {article['content']}

[요청 사항]
1. [요약]: 기사의 핵심 내용을 3줄로 요약해주세요.
2. [신뢰도]: 기사의 신뢰도를 '높음', '보통', '낮음' 중 하나로 평가하고, 그 이유를 한 문장으로 설명해주세요. (형식: [평가 등급] - [평가 이유])
"""
    messages = [
        {"role": "system", "content": "당신은 뉴스 기사를 [요약]과 [신뢰도] 두 항목으로 나누어 분석하고, 지정된 형식에 맞춰 결과를 출력하는 AI입니다."},
        {"role": "user", "content": prompt_text}
    ]
    try:
        # 💡 'await'를 사용하여 비동기적으로 API를 호출합니다.
        completion = await async_client.chat.completions.create(
            model="gpt-5-nano", messages=messages, max_completion_tokens=1500, temperature=0.3
        )
        response_text = completion.choices[0].message.content.strip()
        
        summary_match = re.search(r'\[요약\](.*?)(?=\[신뢰도\]|\Z)', response_text, re.DOTALL)
        reliability_match = re.search(r'\[신뢰도\]\s*(높음|보통|낮음)\s*-\s*(.*)', response_text, re.DOTALL)
        
        summary = summary_match.group(1).strip() if summary_match else "요약 실패"
        if reliability_match:
            grade = reliability_match.group(1).strip()
            reason = reliability_match.group(2).strip()
        else:
            grade = "평가 실패"
            reason = "신뢰도 정보를 파싱하지 못했습니다."
            
        return {"summary": summary, "reliability_grade": grade, "reliability_reason": reason}
    except Exception as e:
        return {"summary": "GPT 오류", "reliability_grade": "오류", "reliability_reason": str(e)}

# ================================
# 5. API 엔드포인트(Endpoint) 정의
# ================================
# '/options' 주소로 GET 요청이 오면, 선택 가능한 언론사와 카테고리 목록을 반환합니다.
@app.get("/options", summary="선택 가능한 언론사 및 카테고리 목록 조회")
def get_options():
    """프론트엔드에서 사용자에게 선택지를 보여주기 위해 사용할 수 있는 API입니다."""
    return {"all_sources": all_sources, "categories": categories}

# '/analyze' 주소로 POST 요청이 오면, 뉴스 분석을 시작합니다.
@app.post("/analyze", summary="뉴스 분석 요청", response_model=Dict[str, List[EvaluatedArticle]])
async def analyze_news(request: AnalysisRequest):
    """사용자로부터 언론사 및 카테고리 목록을 받아 뉴스 분석을 수행하고 결과를 반환합니다."""
    
    # 사용자가 선택한 카테고리가 유효한지 확인합니다.
    for cat in request.selected_categories:
        if cat not in categories:
            raise HTTPException(status_code=400, detail=f"'{cat}'은(는) 유효하지 않은 카테고리입니다.")

    final_results = {}
    
    # 사용자가 선택한 모든 카테고리에 대해 분석을 수행합니다.
    for main_category in request.selected_categories:
        for sub_category in categories[main_category]:
            # 1. 뉴스 기사 수집
            articles_to_evaluate = fetch_news(sub_category)
            if not articles_to_evaluate: continue

            # 2. 💡 수집된 모든 기사에 대해 GPT 평가 작업을 비동기적으로 동시에 실행
            evaluation_tasks = [gpt_evaluate_async(article) for article in articles_to_evaluate]
            evaluations = await asyncio.gather(*evaluation_tasks)

            # 3. 원본 기사 정보와 GPT 평가 결과를 합치기
            evaluated_articles = []
            for article, evaluation in zip(articles_to_evaluate, evaluations):
                evaluated_articles.append(
                    EvaluatedArticle(
                        title=article['title'],
                        link=article['link'],
                        source=article['source'],
                        date=article['date'],
                        summary=evaluation['summary'],
                        reliability_grade=evaluation['reliability_grade'],
                        reliability_reason=evaluation['reliability_reason']
                    )
                )
            
            result_key = f"{main_category} - {sub_category}"
            final_results[result_key] = evaluated_articles

    if not final_results:
        raise HTTPException(status_code=404, detail="선택한 카테고리에서 분석할 뉴스를 찾을 수 없습니다.")

    return final_results

