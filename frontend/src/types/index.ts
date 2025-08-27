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
  | '한국경제';

// ▼▼▼ [수정] '알 수 없음' 상태를 추가합니다. ▼▼▼
export type Reliability = '높음' | '보통' | '낮음' | '알 수 없음';
// ▲▲▲ [수정] ▲▲▲

export type NewsCategory = '정치' | '경제' | '사회' | 'IT_과학' | '생활_문화' | '세계';

export type NewsArticle = {
  category: NewsCategory;
  title: string;
  link: string;
  source: Publisher;
  date: string;
  summary: string;
  reliability: Reliability;
  evaluation?: string;
};
