import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup

# ================================
# 1. 설정
# ================================
# 사용자께서 알려주신 뉴스 파일 저장 경로
output_directory = 'C:/Users/admin/Desktop/news/test1/output'
NEWS_DATA = [] # 뉴스 데이터를 메모리에 저장할 리스트

# ================================
# 2. Flask 앱 초기화
# ================================
app = Flask(__name__)
# 프론트엔드와 통신하기 위해 CORS 설정
CORS(app) 

# ================================
# 3. 서버 시작 시 뉴스 데이터 미리 불러오기
# ================================
def load_news_data():
    """
    서버가 시작될 때 output 폴더의 모든 HTML 파일에서 기사 정보를 읽어
    NEWS_DATA 리스트에 저장합니다. 검색 속도를 높이기 위한 전처리 과정입니다.
    """
    global NEWS_DATA
    if NEWS_DATA: # 데이터가 이미 로드된 경우 중복 실행 방지
        return

    print("서버 시작 전 뉴스 데이터 로딩 중...")
    html_files = []
    for dirpath, _, filenames in os.walk(output_directory):
        for filename in filenames:
            if filename.endswith('_news.html'):
                html_files.append(os.path.join(dirpath, filename))

    for file_path in html_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                articles = soup.select('.article-block')
                
                for article in articles:
                    title_tag = article.select_one('h3 a')
                    image_tag = article.select_one('.article-image')
                    source_tag = article.select_one('p')
                    summary_tag = article.select_one('.summary')

                    # 데이터가 없는 경우를 대비해 안전하게 추출
                    title = title_tag.text if title_tag else "제목 없음"
                    link = title_tag['href'] if title_tag and title_tag.has_attr('href') else "#"
                    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None
                    
                    source_info = source_tag.text.split('|') if source_tag else []
                    source = source_info[0].replace('언론사:', '').strip() if len(source_info) > 0 else ""
                    date = source_info[1].replace('발행 시간:', '').strip() if len(source_info) > 1 else ""
                    
                    summary_text = ""
                    reliability = ""
                    if summary_tag:
                        reliability_span = summary_tag.select_one('.reliability')
                        if reliability_span:
                            reliability = reliability_span.text.replace('신뢰도:', '').strip()
                            reliability_span.decompose() # 신뢰도 태그는 텍스트에서 제외
                        summary_text = summary_tag.text.strip()
                    
                    NEWS_DATA.append({
                        'title': title,
                        'link': link,
                        'imageUrl': image_url,
                        'source': source,
                        'date': date,
                        'summary': summary_text,
                        'reliability': reliability,
                        # 검색 효율을 위해 주요 텍스트를 합쳐서 저장
                        'searchText': f"{title} {summary_text} {source}".lower()
                    })
        except Exception as e:
            print(f"'{file_path}' 파일 처리 중 오류 발생: {e}")

    print(f"✅ 총 {len(NEWS_DATA)}개의 뉴스 기사 로딩 완료.")

# ================================
# 4. 검색 API 엔드포인트 생성
# ================================
@app.route('/search')
def search_news():
    """
    '/search?q=검색어' 형태로 요청이 오면 검색 결과를 JSON으로 반환합니다.
    """
    query = request.args.get('q', '').lower().strip()

    if not query:
        return jsonify({"error": "검색어가 필요합니다."}), 400

    print(f"'{query}' 검색 요청 수신")
    
    # 미리 로드된 NEWS_DATA에서 'searchText' 필터를 사용해 검색
    search_results = [
        article for article in NEWS_DATA if query in article['searchText']
    ]
    
    print(f"'{query}'에 대한 검색 결과: {len(search_results)}건")

    return jsonify(search_results)

# ================================
# 5. 서버 실행
# ================================
if __name__ == '__main__':
    # 서버를 실행하기 전에 뉴스 데이터 로딩 함수를 먼저 호출
    load_news_data()
    # 서버 실행 (debug=True는 개발용, 실제 Azure 배포 시에는 gunicorn이 실행)
    app.run(host='0.0.0.0', port=5000, debug=True)