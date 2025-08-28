import feedparser
import time
import os
from datetime import datetime, timedelta
from urllib.parse import quote
from openai import AzureOpenAI
import re

# ================================
# 1. 전체 뉴스/카테고리 목록
# ================================
all_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
    '오마이뉴스', '한국경제', '매일경제', '프레시안', '머니투데이'
]

categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계']
}

MAX_ARTICLES_PER_CATEGORY = 100
save_path = './output'

one_month_ago = datetime.now() - timedelta(days=30)
os.makedirs(save_path, exist_ok=True)

# ================================
# 2. Azure OpenAI 초기화
# ================================
endpoint = "https://newscheck2.openai.azure.com/"
deployment = "gpt-5-nano"
api_key = "Dsf5DmuTn1cS7lXaSxSTnO30kTZCqr2xKqIjLwvdovEGnQsz3NjlJQQJ99BHACHYHv6XJ3w3AAABACOGJk53"

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2025-01-01-preview",
)

# ================================
# 3. 사용자 설정 함수
# ================================
def get_user_preferences():
    """사용자로부터 언론사(5개)와 뉴스 카테고리(무제한)를 입력받는 함수"""
    print("📰 분석을 원하는 언론사 5개를 선택해주세요. (쉼표(,)로 구분)")
    for i, source in enumerate(all_sources):
        print(f"{i+1}. {source}", end='  ')
    print("\n")
    
    selected_sources = []
    while len(selected_sources) != 5:
        try:
            user_input = input(">> 선택 (번호 또는 이름 5개 입력): ")
            inputs = [item.strip() for item in user_input.split(',')]
            
            if len(inputs) != 5:
                print("🚨 반드시 5개의 언론사를 선택해야 합니다. 다시 입력해주세요.")
                continue

            temp_sources = []
            valid_input = True
            for item in inputs:
                if item.isdigit() and 1 <= int(item) <= len(all_sources):
                    temp_sources.append(all_sources[int(item) - 1])
                elif item in all_sources:
                    temp_sources.append(item)
                else:
                    print(f"🚨 '{item}'은(는) 잘못된 입력입니다. 목록에 있는 번호나 이름을 입력해주세요.")
                    valid_input = False
                    break
            
            if valid_input:
                unique_sources = sorted(list(set(temp_sources)))
                if len(unique_sources) == 5:
                    selected_sources = unique_sources
                else:
                    print("🚨 중복된 선택이 있거나, 5개가 아닙니다. 다시 선택해주세요.")
        except ValueError:
            print("🚨 잘못된 입력입니다. 다시 시도해주세요.")
    
    print(f"\n✅ 선택된 언론사: {', '.join(selected_sources)}\n")

    print("📚 수집을 원하는 뉴스 카테고리를 선택해주세요. (갯수 제한 없음, 여러 개 선택 시 쉼표(,)로 구분)")
    category_keys = list(categories.keys())
    for i, cat in enumerate(category_keys):
        print(f"{i+1}. {cat}", end='  ')
    print("\n")

    selected_categories = []
    while not selected_categories:
        try:
            user_input = input(">> 선택 (번호 또는 이름 입력): ")
            inputs = [item.strip() for item in user_input.split(',')]
            for item in inputs:
                if item.isdigit() and 1 <= int(item) <= len(category_keys):
                    selected_categories.append(category_keys[int(item) - 1])
                elif item in category_keys:
                    selected_categories.append(item)
            if not selected_categories:
                print("🚨 잘못된 입력입니다. 목록에 있는 번호나 이름을 입력해주세요.")
        except ValueError:
            print("🚨 잘못된 입력입니다. 다시 시도해주세요.")

    selected_categories = sorted(list(set(selected_categories)))
    print(f"\n✅ 선택된 카테고리: {', '.join(selected_categories)}\n")
    
    return selected_sources, selected_categories

# ================================
# 4. 뉴스 수집 함수
# ================================
def fetch_news(sub_category, main_category):
    encoded_keyword = quote(sub_category)
    news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(news_url)

    articles = []
    saved_count = 0

    for entry in feed.entries:
        if saved_count >= MAX_ARTICLES_PER_CATEGORY:
            break

        source_name = getattr(entry, 'source', None)
        if source_name and source_name.title in all_sources:
            published_time = entry.get('published_parsed')
            if not published_time:
                continue
            
            article_date = datetime.fromtimestamp(time.mktime(published_time))
            if article_date < one_month_ago:
                continue

            content = re.sub('<[^<]+?>', '', entry.summary if hasattr(entry, 'summary') else entry.title)

            articles.append({
                'title': entry.title,
                'link': entry.link,
                'source': source_name.title,
                'date': article_date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': content
            })
            saved_count += 1
    return articles

# ================================
# 5. GPT 평가 함수 (수정됨)
# ================================
def gpt_evaluate(article, selected_sources):
    """GPT를 사용하여 기사를 요약하고 신뢰도를 평가하는 함수 (프롬프트 개선)"""
    # 프롬프트를 더 명확하고 구조적으로 변경하여 모델이 지시를 더 잘 따르도록 함
    prompt_text = f"""
당신은 뉴스 기사를 객관적으로 분석하는 AI입니다. 아래 요청사항에 따라 기사를 분석하고, 반드시 지정된 형식으로만 출력해주세요.

[분석할 뉴스 기사]
- 제목: {article['title']}
- 내용: {article['content']}

[요청 사항]
1. [요약]: 기사의 핵심 내용을 3줄로 요약해주세요.
2. [신뢰도]: 기사의 신뢰도를 '높음', '보통', '낮음' 중 하나로 평가하고, 그 이유를 한 문장으로 설명해주세요. (형식: [평가 등급] - [평가 이유])

[신뢰도 평가 기준]
- 높음: 사실 관계가 명확하고, 여러 출처에서 교차 확인이 가능하며, 객관적인 논조를 유지하는 경우.
- 보통: 사실에 기반하지만 특정 관점이 두드러지거나, 일부 주장에 대한 근거가 부족한 경우.
- 낮음: 감정적이거나 자극적인 표현을 사용하고, 확인되지 않은 사실을 전달하거나, 명백한 편향성을 보이는 경우.
"""
    messages = [
        {"role": "system", "content": "당신은 뉴스 기사를 [요약]과 [신뢰도] 두 항목으로 나누어 분석하고, 지정된 형식에 맞춰 결과를 출력하는 AI입니다."},
        {"role": "user", "content": prompt_text}
    ]

    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=1500,
            temperature=0.3, # 더 사실에 기반한 답변을 위해 온도를 낮춤
        )
        result_text = completion.choices[0].message.content.strip()
        return result_text
    except Exception as e:
        return f"GPT 평가 오류: {e}"

# ================================
# 6. HTML 저장 함수 (수정됨)
# ================================
def save_news_to_html(main_category, sub_category, articles):
    """수집하고 평가한 뉴스 기사를 HTML 파일로 저장하는 함수"""
    main_path = os.path.join(save_path, main_category)
    os.makedirs(main_path, exist_ok=True)
    
    safe_sub_category = sub_category.replace('/', '_').replace('\\', '_')
    file_name = f"{safe_sub_category}_news.html"
    full_path = os.path.join(main_path, file_name)

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'>")
        f.write(f"<title>{main_category} - {sub_category} 뉴스</title>")
        f.write("<style>")
        f.write("""
            body { font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; margin: 20px; background-color: #f4f4f9; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .article { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .article h3 a { color: #3498db; text-decoration: none; }
            .article h3 a:hover { text-decoration: underline; }
            .meta { font-size: 0.9em; color: #7f8c8d; margin-bottom: 15px; }
            .evaluation { background-color: #ecf0f1; border-left: 4px solid #3498db; padding: 15px; margin-top: 15px; border-radius: 4px; }
            .reliability { font-weight: bold; padding: 3px 8px; border-radius: 12px; color: white; font-size: 0.9em; }
            .high { background-color: #2ecc71; }
            .medium { background-color: #f39c12; }
            .low { background-color: #e74c3c; }
        """)
        f.write("</style></head><body>\n")
        f.write(f"<h1>{main_category} - {sub_category}</h1>\n")

        if not articles:
            f.write("<p>해당 카테고리에서 수집된 뉴스가 없습니다.</p>")

        for article in articles:
            evaluation_text = article.get('evaluation', '')
            
            # 더 안정적인 파싱을 위해 정규 표현식 수정
            summary_match = re.search(r'\[요약\](.*?)(?=\[신뢰도\]|\Z)', evaluation_text, re.DOTALL)
            reliability_match = re.search(r'\[신뢰도\]\s*(높음|보통|낮음)\s*-\s*(.*)', evaluation_text, re.DOTALL)

            summary = summary_match.group(1).strip().replace('\n', '<br>') if summary_match else "요약 정보를 가져오는 데 실패했습니다."
            
            reliability_grade = "평가 실패"
            reliability_reason = ""
            reliability_class = ""

            if reliability_match:
                reliability_grade = reliability_match.group(1).strip()
                reliability_reason = reliability_match.group(2).strip()
                if reliability_grade == "높음": reliability_class = "high"
                elif reliability_grade == "보통": reliability_class = "medium"
                elif reliability_grade == "낮음": reliability_class = "low"
            else:
                # GPT 응답 전체를 이유로 표시하여 디버깅에 용이하게 함
                reliability_reason = f"신뢰도 정보를 파싱하는 데 실패했습니다. (원본 응답: {evaluation_text})"

            f.write("<div class='article'>\n")
            f.write(f"<h3><a href='{article['link']}' target='_blank' rel='noopener noreferrer'>{article['title']}</a></h3>\n")
            f.write(f"<p class='meta'><b>언론사:</b> {article['source']} | <b>발행 시간:</b> {article['date']}</p>\n")
            f.write("<div class='evaluation'>\n")
            f.write(f"<p><b>🤖 AI 요약:</b><br>{summary}</p>\n")
            f.write(f"<p><b>⭐ 신뢰도 평가:</b> <span class='reliability {reliability_class}'>{reliability_grade}</span> - {reliability_reason}</p>\n")
            f.write("</div>\n</div>\n")

        f.write("</body></html>")

# ================================
# 7. 메인 실행 루프
# ================================
if __name__ == "__main__":
    user_selected_sources, user_follow_categories = get_user_preferences()

    print("\n🚀 뉴스 수집 및 분석을 시작합니다...\n")
    
    for main_category in user_follow_categories:
        sub_categories = categories.get(main_category, [])
        for sub_category in sub_categories:
            print(f"[{main_category}] '{sub_category}' 뉴스 수집 중...")
            articles = fetch_news(sub_category, main_category)

            if not articles:
                print(f"  -> 수집된 뉴스가 없습니다.")
                continue

            print(f"  -> {len(articles)}개 뉴스 수집 완료. GPT 평가 시작...")
            for i, article in enumerate(articles):
                print(f"    - 기사 {i+1}/{len(articles)} 평가 중...")
                article['evaluation'] = gpt_evaluate(article, user_selected_sources)
                time.sleep(1)

            save_news_to_html(main_category, sub_category, articles)
            print(f"  -> '{sub_category}' 뉴스 저장 완료.\n")

    print("\n🎉 모든 작업이 완료되었습니다! 'output' 폴더를 확인해주세요.")
