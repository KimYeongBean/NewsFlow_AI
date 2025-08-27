export interface NewsArticle {
  id: number;
  title: string;
  link: string;
  publisher: string; // 백엔드의 source 필드에 해당
  source: string; // NewsCard에서 publisher 대신 source를 사용하도록 변경
  description: string; // 백엔드의 summary 필드에 해당
  summary: string;
  imageSrc: string; // 이 필드는 API 응답에 없으므로, 정적 이미지나 기본값을 사용해야 함
  publishedDate: string; // 백엔드의 date 필드에 해당
  date: string;
  category: '경제' | '사회' | '정치' | 'IT/기술' | '문화' | '세계';
  reliability: '높음' | '보통' | '낮음' | '알 수 없음' | '오류';
  reliability_class: 'high' | 'medium' | 'low' | 'error';
}

export type Publisher = 'KBS' | 'MBC' | 'SBS' | '헤럴드경제' | '한겨레';