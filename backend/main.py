# ================================
# 0. 라이브러리 불러오기
# ================================
# FastAPI 프레임워크와 API 오류 처리를 위한 HTTPException을 가져옵니다.
from fastapi import FastAPI, HTTPException
# 데이터 유효성 검사를 위한 BaseModel과 필드 설정을 위한 Field를 가져옵니다.
from pydantic import BaseModel, Field
# 타입 힌팅(Type Hinting)을 위해 List와 Dict를 가져옵니다. 코드의 가독성을 높여줍니다.
from typing import List, Dict
# 웹사이트의 RSS 피드를 파싱(분석)하기 위한 feedparser 라이브러리를 가져옵니다.
import feedparser
# 날짜와 시간을 다루기 위한 datetime과 timedelta를 가져옵니다.
from datetime import datetime, timedelta
# URL에 한글 등 비ASCII 문자를 안전하게 포함시키기 위한 quote 함수를 가져옵니다.
from urllib.parse import quote
# Azure OpenAI API를 비동기적으로 사용하기 위한 AsyncAzureOpenAI 클라이언트를 가져옵니다.
from openai import AsyncAzureOpenAI
# 정규 표현식(Regular Expression)을 사용하기 위한 re 라이브러리를 가져옵니다.
import re
# 비동기 작업을 처리하기 위한 asyncio 라이브러리를 가져옵니다.
import asyncio
# 프로그램 실행 시간 측정 등 시간 관련 기능을 사용하기 위한 time 라이브러리를 가져옵니다.
import time

# ================================
# 1. FastAPI 앱 초기화 및 기본 설정
# ================================
# FastAPI 애플리케이션의 메인 객체를 생성합니다. 이 객체를 통해 API 서버가 동작합니다.
app = FastAPI(
    # API 문서에 표시될 제목을 설정합니다.
    title="뉴스 분석 API (News Analyzer API)",
    # API 문서에 표시될 상세 설명을 설정합니다.
    description="선택한 언론사와 카테고리를 기반으로 뉴스를 수집하고 AI로 요약 및 신뢰도를 평가하는 API입니다.",
    # API의 버전을 설정합니다.
    version="2.0.0"
)

# 분석 대상 및 사용자가 선택할 수 있는 전체 언론사 목록을 리스트로 정의합니다.
all_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제', '매일경제', '프레시안', '머니투데이'
]

# 뉴스 카테고리를 대분류(Key)와 세부 카테고리 리스트(Value)로 구성된 딕셔너리로 정의합니다.
categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계']
}

# 💡 프론트엔드에서 사용하기 편하도록 모든 세부 카테고리를 하나의 리스트로 만듭니다.
# 리스트 컴프리헨션(List Comprehension)을 사용하여 간결하게 작성되었습니다.
all_sub_categories = [sub for main in categories.values() for sub in main]

# 하나의 세부 카테고리당 수집할 최대 기사 수를 10개로 제한합니다.
MAX_ARTICLES_PER_CATEGORY = 10
# 현재 시간으로부터 30일 이전의 날짜를 계산하여, 이보다 오래된 기사는 수집에서 제외합니다.
one_month_ago = datetime.now() - timedelta(days=30)

# ================================
# 2. Azure OpenAI 비동기 클라이언트 초기화
# ================================
# Azure OpenAI 서비스에 연결하기 위한 비동기 클라이언트 객체를 생성합니다.
async_client = AsyncAzureOpenAI(
    # Azure에 배포된 OpenAI 서비스의 고유 주소(엔드포인트)입니다.
    azure_endpoint="https://newscheck2.openai.azure.com/",
    # 서비스에 접근하기 위한 API 인증 키입니다.
    api_key="Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53",
    # 사용할 API의 버전입니다.
    api_version="2025-01-01-preview",
)

# ================================
# 3. API 데이터 모델 정의 (Pydantic) - 수정됨
# ================================
# API가 요청(Request)을 받을 때 데이터의 형식을 검증하기 위한 모델을 정의합니다.
class AnalysisRequest(BaseModel):
    # 'selected_sources'는 문자열(str)로 이루어진 리스트(List)여야 합니다.
    # Field의 '...'는 이 필드가 필수값임을 의미하며, min/max_length로 개수를 5개로 강제합니다.
    selected_sources: List[str] = Field(..., description="분석 기준으로 삼을 언론사 5개의 목록", min_length=5, max_length=5)
    # 💡 이제 상위 카테고리가 아닌, 세부 카테고리를 직접 리스트로 받습니다.
    # 'selected_sub_categories'는 문자열 리스트이며, 최소 1개 이상이어야 합니다.
    selected_sub_categories: List[str] = Field(..., description="수집을 원하는 세부 카테고리 목록 (최소 1개 이상)", min_length=1)

# API가 응답(Response)을 보낼 때 데이터의 형식을 정의하는 모델입니다.
class EvaluatedArticle(BaseModel):
    # 각 필드가 어떤 타입이어야 하는지 지정합니다. (예: title은 반드시 문자열이어야 함)
    title: str
    link: str
    source: str
    date: str
    summary: str
    reliability_grade: str
    reliability_reason: str

# ================================
# 4. 핵심 로직 함수 (gpt_evaluate_async 강화)
# ================================
# 뉴스 기사를 수집하는 함수를 정의합니다.
def fetch_news(sub_category: str) -> List[Dict]:
    # URL에 한글 키워드를 포함시키기 위해 UTF-8 인코딩을 합니다.
    encoded_keyword = quote(sub_category)
    # 구글 뉴스 RSS 검색을 위한 URL을 생성합니다.
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    # feedparser로 해당 URL의 RSS 데이터를 파싱합니다.
    feed = feedparser.parse(news_url)
    # 수집된 기사를 저장할 빈 리스트를 생성합니다.
    articles = []
    # RSS 피드에 포함된 모든 기사 항목(entry)을 순회합니다.
    for entry in feed.entries:
        # 최대 수집 개수에 도달하면 반복을 중단합니다.
        if len(articles) >= MAX_ARTICLES_PER_CATEGORY: break
        # 기사의 출처(언론사) 정보를 가져옵니다. 없으면 None이 됩니다.
        source_name = getattr(entry, 'source', None)
        # 언론사 정보가 있고, 우리가 정의한 언론사 목록에 포함된 경우에만 처리합니다.
        if source_name and source_name.title in all_sources:
            # 기사의 발행 시간을 가져옵니다.
            published_time = entry.get('published_parsed')
            # 발행 시간이 없으면 이 기사는 건너뜁니다.
            if not published_time: continue
            # 발행 시간을 파이썬 datetime 객체로 변환합니다.
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            # 기사가 30일보다 오래되었으면 건너뜁니다.
            if article_date < one_month_ago: continue
            # 기사 본문/요약에서 HTML 태그를 정규표현식으로 모두 제거합니다.
            content = re.sub('<[^<]+?>', '', entry.summary if hasattr(entry, 'summary') else entry.title)
            # 필요한 정보만 담은 딕셔너리를 생성하여 articles 리스트에 추가합니다.
            articles.append({
                'title': entry.title, 'link': entry.link, 'source': source_name.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'), 'content': content
            })
    # 최종적으로 수집된 기사 리스트를 반환합니다.
    return articles

# 💡 GPT 평가 함수를 비동기(async) 함수로 정의하여 여러 요청을 동시에 처리할 수 있게 합니다.
async def gpt_evaluate_async(article: Dict) -> Dict:
    # GPT에게 전달할 프롬프트(지시문)를 f-string 형식으로 생성합니다.
    prompt_text = f"""
[분석할 뉴스 기사]
- 제목: {article['title']}
- 내용: {article['content']}

[요청 사항]
1. [요약]: 기사의 핵심 내용을 3줄로 요약해주세요.
2. [신뢰도]: 기사의 신뢰도를 '높음', '보통', '낮음' 중 하나로 평가하고, 그 이유를 한 문장으로 설명해주세요. (형식: [평가 등급] - [평가 이유])
"""
    # OpenAI API가 요구하는 대화 형식(messages)으로 프롬프트를 구성합니다.
    messages = [
        {"role": "system", "content": "당신은 뉴스 기사를 [요약]과 [신뢰도] 두 항목으로 나누어 분석하고, 지정된 형식에 맞춰 결과를 출력하는 AI입니다."},
        {"role": "user", "content": prompt_text}
    ]
    # API 호출 시 발생할 수 있는 예외를 처리하기 위해 try-except 블록을 사용합니다.
    try:
        # 'await' 키워드를 사용하여 비동기적으로 OpenAI API를 호출하고 응답이 올 때까지 기다립니다.
        completion = await async_client.chat.completions.create(
            model="gpt-5-nano", messages=messages, max_completion_tokens=1500, temperature=0.3
        )
        # API 응답에서 텍스트 부분만 추출하고 앞뒤 공백을 제거합니다.
        response_text = completion.choices[0].message.content.strip()
        
        # 💡 파싱 로직 강화: 정규표현식을 사용하여 GPT 응답에서 '[요약]' 부분을 찾습니다.
        summary_match = re.search(r'\[요약\](.*?)(?=\[신뢰도\]|\Z)', response_text, re.DOTALL)
        # 요약 부분을 찾았으면 해당 내용을, 못 찾았으면 실패 메시지를 summary 변수에 저장합니다.
        summary = summary_match.group(1).strip() if summary_match else "요약 정보를 찾지 못했습니다."

        # 정규표현식을 사용하여 GPT 응답에서 '[신뢰도]' 부분과 등급, 이유를 찾습니다.
        reliability_match = re.search(r'\[신뢰도\]\s*(높음|보통|낮음)\s*-\s*(.*)', response_text, re.DOTALL)
        # 신뢰도 부분을 찾았으면 등급과 이유를 각각 변수에 저장합니다.
        if reliability_match:
            grade = reliability_match.group(1).strip()
            reason = reliability_match.group(2).strip()
        # 못 찾았으면 실패 상태와 원본 응답의 일부를 저장하여 디버깅을 돕습니다.
        else:
            grade = "평가 실패"
            reason = f"신뢰도 정보를 파싱하지 못했습니다. [원본 응답: {response_text[:100]}...]"
            
        # 최종 분석 결과를 딕셔너리 형태로 반환합니다.
        return {"summary": summary, "reliability_grade": grade, "reliability_reason": reason}
    # API 호출이나 다른 과정에서 오류가 발생했을 경우
    except Exception as e:
        # 오류 내용을 포함한 실패 결과를 딕셔너리 형태로 반환합니다.
        return {"summary": "GPT API 오류", "reliability_grade": "오류", "reliability_reason": f"API 호출 중 오류 발생: {str(e)}"}

# ================================
# 5. API 엔드포인트(Endpoint) 정의 - 수정됨
# ================================
# '/options' 경로로 GET 요청이 왔을 때 실행될 함수를 정의합니다.
@app.get("/options", summary="선택 가능한 언론사 및 카테고리 목록 조회")
def get_options():
    """프론트엔드에서 사용자에게 선택지를 보여주기 위해 사용할 수 있는 API입니다."""
    # 💡 이제 세분화된 카테고리 목록을 제공합니다.
    return {"all_sources": all_sources, "all_sub_categories": all_sub_categories}

# '/analyze' 경로로 POST 요청이 왔을 때 실행될 비동기 함수를 정의합니다.
@app.post("/analyze", summary="뉴스 분석 요청", response_model=Dict[str, List[EvaluatedArticle]])
async def analyze_news(request: AnalysisRequest):
    """사용자로부터 언론사 및 세부 카테고리 목록을 받아 뉴스 분석을 수행하고 결과를 반환합니다."""
    
    # 사용자가 요청한 세부 카테고리가 우리가 정의한 목록에 있는지 하나씩 확인합니다.
    for sub_cat in request.selected_sub_categories:
        # 만약 유효하지 않은 카테고리가 있다면, 400 오류 코드와 함께 에러 메시지를 반환합니다.
        if sub_cat not in all_sub_categories:
            raise HTTPException(status_code=400, detail=f"'{sub_cat}'은(는) 유효하지 않은 세부 카테고리입니다.")

    # 최종 결과를 담을 빈 딕셔너리를 생성합니다.
    final_results = {}
    
    # 💡 이제 사용자가 선택한 세부 카테고리 목록을 직접 순회합니다.
    for sub_category in request.selected_sub_categories:
        # 해당 카테고리의 뉴스 기사를 수집합니다.
        articles_to_evaluate = fetch_news(sub_category)
        # 수집된 기사가 없으면 다음 카테고리로 넘어갑니다.
        if not articles_to_evaluate: continue

        # 수집된 모든 기사에 대해 GPT 평가 비동기 작업을 리스트로 만듭니다. (아직 실행 전)
        evaluation_tasks = [gpt_evaluate_async(article) for article in articles_to_evaluate]
        # asyncio.gather를 사용하여 모든 평가 작업을 동시에 실행하고, 모든 결과가 올 때까지 기다립니다.
        evaluations = await asyncio.gather(*evaluation_tasks)

        # 원본 기사 정보(article)와 GPT 평가 결과(evaluation)를 짝지어 최종 응답 모델에 맞게 정리합니다.
        evaluated_articles = [
            EvaluatedArticle(
                title=article['title'], link=article['link'], source=article['source'],
                date=article['date'], summary=evaluation['summary'],
                reliability_grade=evaluation['reliability_grade'],
                reliability_reason=evaluation['reliability_reason']
            )
            for article, evaluation in zip(articles_to_evaluate, evaluations)
        ]
        
        # 결과 딕셔너리에 세부 카테고리 이름을 Key로 하여 분석된 기사 리스트를 저장합니다.
        final_results[sub_category] = evaluated_articles

    # 모든 카테고리를 처리했는데도 결과가 하나도 없으면, 404 오류를 반환합니다.
    if not final_results:
        raise HTTPException(status_code=404, detail="선택한 카테고리에서 분석할 뉴스를 찾을 수 없습니다.")

    # 최종 결과를 JSON 형태로 클라이언트에게 반환합니다.
    return final_results
