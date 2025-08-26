// 언론사 타입을 미리 정의
export type Publisher = 'KBS' | 'MBC' | 'SBS' | '헤럴드경제' | '한겨레' | '조선일보' | '뉴스1' | '연합뉴스' | '비즈니스포스트' | '채널A' | 'MBN 홈페이지' | '쿠키뉴스' | '프레시안' | 'IT조선' | '컬처데일리';

export type NewsArticle = {
  id: number;
  category: '경제' | '사회' | '정치' | 'IT/기술' | '문화' | '세계';
  imageSrc: string;
  publisher: Publisher; // 'string' 대신 미리 정의한 'Publisher' 타입을 사용
  title: string;
  description: string;
  link: string;
  publishedDate: string;
};
