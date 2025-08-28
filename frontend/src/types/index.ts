export type Publisher =
  | 'MBC뉴스'
  | '연합뉴스'
  | '조선일보'
  | '뉴스1'
  | 'JTBC 뉴스'
  | '중앙일보'
  | 'SBS 뉴스'
  | 'YTN'
  | '한겨레'
  | '경향신문'
  | '오마이뉴스'
  | '한국경제'
  | '알 수 없음'; 

export type Reliability = '높음' | '보통' | '낮음' | '알 수 없음';

// ▼▼▼ [수정] HTML 구조에 맞춰 지원하는 언어 코드를 타입으로 정의합니다. ▼▼▼
export type LanguageCode = 'ko' | 'en' | 'ja' | 'fr' | 'zh-Hans';
// ▲▲▲ [수정] ▲▲▲

/**
 * 뉴스 대분류 카테고리 타입
 */
export type NewsCategory = '전체' | '정치' | '경제' | '사회' | 'IT_과학' | '생활_문화' | '세계' | '여행';

/**
 * 뉴스 소분류 카테고리 타입
 */
export type NewsSubCategory =
  // 정치
  | '대통령실' | '국회' | '정당' | '행정' | '외교' | '국방/북한'
  // 경제
  | '금융/증권' | '산업/재계' | '중기/벤처' | '부동산' | '글로벌' | '생활'
  // 사회
  | '사건사고' | '교육' | '노동' | '언론' | '환경' | '인권/복지' | '식품/의료' | '지역' | '인물'
  // IT_과학
  | '모바일' | '인터넷/SNS' | '통신/뉴미디어' | 'IT' | '보안/해킹' | '컴퓨터' | '게임/리뷰' | '과학'
  // 생활_문화
  | '건강' | '자동차' | '여행/레저' | '음식/맛집' | '패션/뷰티' | '공연/전시' | '책' | '종교' | '날씨' | '생활'
  // 세계
  | '아시아/호주' | '미국/중남미' | '유럽' | '중동/아프리카' | '세계'
  // 여행
  | '국내 여행' ;

/**
 * 앱 전체에서 사용할 카테고리 구조 데이터
 */
export const CATEGORIES: { readonly [key in NewsCategory]: readonly NewsSubCategory[] } = {
  '전체': [],
  '정치': ['대통령실', '국회', '정당', '행정', '외교', '국방/북한'],
  '경제': ['금융/증권', '산업/재계', '중기/벤처', '부동산', '글로벌', '생활'],
  '사회': ['사건사고', '교육', '노동', '언론', '환경', '인권/복지', '식품/의료', '지역', '인물'],
  'IT_과학': ['모바일', '인터넷/SNS', '통신/뉴미디어', 'IT', '보안/해킹', '컴퓨터', '게임/리뷰', '과학'],
  '생활_문화': ['건강', '자동차', '여행/레저', '음식/맛집', '패션/뷰티', '공연/전시', '책', '종교', '날씨', '생활'],
  '세계': ['아시아/호주', '미국/중남미', '유럽', '중동/아프리카', '세계'],
  '여행': ['국내 여행']
};

/**
 * 개별 뉴스 기사 데이터 구조 타입
 * HTML의 다국어 제목 구조를 반영하여 수정합니다.
 */
export type NewsArticle = {
  // 백엔드에서 임의의 카테고리명을 보낼 수 있으므로 string으로 수용합니다.
  category: string;
  subCategory: string;

  // DB의 고유 id가 있으면 표시
  id?: string;

  // 다국어 제목/요약 구조
  translatedTitles: Record<LanguageCode, string>;
  translatedSummaries?: Record<LanguageCode, string>;
  imageUrl?: string;

  link: string;
  // 언론사명은 자유 텍스트로 올 수 있으므로 string으로 수용
  source: string;
  date: string;
  summary: string;
  reliability: Reliability;
  evaluation?: string;
};
