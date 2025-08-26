import feedparser
import time
import os
from datetime import datetime, timedelta
from urllib.parse import quote

# --- 설정 부분 ---

# 수집을 원하는 언론사 목록
target_sources = [
    'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC News', 
    '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문', 
    '오마이뉴스', '한국경제'
]

# 수집할 뉴스의 대분류 및 세부 카테고리 목록
categories = {
    '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
    '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
    '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
    'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
    '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
    '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계']
}

# 각 세부 카테고리별로 수집할 기사의 최대 개수
MAX_ARTICLES_PER_CATEGORY = 100

# 수집한 파일을 저장할 기본 폴더 경로
save_path = "C:/Users/admin/Desktop/news"

# --- 준비 단계 ---

# 현재 날짜를 기준으로 30일 전의 날짜를 계산 (수집 기간 설정)
one_month_ago = datetime.now() - timedelta(days=30)

# 저장할 폴더가 없으면 자동으로 생성
os.makedirs(save_path, exist_ok=True)
print(f"'{save_path}' 폴더에 뉴스를 저장할 준비가 되었습니다.")
print(f"기준 날짜: {one_month_ago.strftime('%Y-%m-%d')} 이후의 기사만 저장합니다.")
print(f"대상 언론사: {', '.join(target_sources)}")
print(f"세부 카테고리별 최대 수집 개수: {MAX_ARTICLES_PER_CATEGORY}개")
print("-" * 60)

# --- 메인 실행 부분 ---

# categories 딕셔너리에서 대분류와 세부 카테고리 리스트를 하나씩 가져와 반복
for main_category, sub_categories in categories.items():
    
    # 대분류 이름으로 폴더 경로를 생성
    main_category_path = os.path.join(save_path, main_category)
    os.makedirs(main_category_path, exist_ok=True)
    print(f"\n📁 '{main_category}' 폴더에서 작업을 시작합니다.")
    
    # 해당 대분류에 속한 세부 카테고리들을 하나씩 반복
    for sub_category in sub_categories:
        print(f"  -> '{sub_category}' 뉴스 수집 중...")
        
        # URL에 한글 키워드를 넣기 위해 인코딩
        encoded_keyword = quote(sub_category)
        news_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR"
        
        # feedparser를 이용해 RSS 피드 정보를 파싱
        feed = feedparser.parse(news_url)
        
        # 파일 이름에 포함될 수 없는 문자를 '_'로 변경
        file_name = f"{sub_category.replace('/', '_')}_news.txt"
        full_path = os.path.join(main_category_path, file_name)
        
        saved_in_category = 0
        
        try:
            # 파일을 쓰기 모드('w')로 열고, 한글 처리를 위해 인코딩 설정
            with open(full_path, 'w', encoding='utf-8') as f:
                # 파싱된 피드에서 각 기사(entry) 정보를 하나씩 반복
                for entry in feed.entries:
                    # 현재 카테고리에서 저장된 기사 수가 최대치를 넘으면 중단
                    if saved_in_category >= MAX_ARTICLES_PER_CATEGORY:
                        break

                    # 기사의 언론사가 target_sources 목록에 포함되어 있는지 확인
                    if entry.source.title in target_sources:
                        published_time = entry.get('published_parsed')
                        if not published_time:
                            continue

                        # 기사 발행 시간을 파이썬 datetime 객체로 변환
                        article_date = datetime.fromtimestamp(time.mktime(published_time))
                        
                        # 기사 발행일이 설정된 기간(최근 한 달) 내에 있는지 확인
                        if article_date >= one_month_ago:
                            # 모든 조건을 만족하면 파일에 정보 저장
                            f.write(f"제목: {entry.title}\n")
                            f.write(f"언론사: {entry.source.title}\n")
                            f.write(f"링크: {entry.link}\n")
                            f.write(f"발행 시간: {article_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("-" * 50 + "\n\n")
                            saved_in_category += 1
            
            print(f"    ✅ '{file_name}' 파일에 {saved_in_category}개의 기사를 저장했습니다.")

        except Exception as e:
            # 오류 발생 시 메시지 출력
            print(f"    🚨 '{sub_category}' 뉴스 저장 중 오류 발생: {e}")

        # 구글 서버에 부담을 주지 않기 위해 1초 대기
        time.sleep(1)

print("\n🎉 모든 뉴스 수집이 완료되었습니다!")