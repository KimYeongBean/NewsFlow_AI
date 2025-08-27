import { NewsArticle } from '@/types';

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}.${month}.${day} ${hours}:${minutes}`;
};

// ▼▼▼ [수정] '알 수 없음' 상태에 대한 스타일을 추가합니다. ▼▼▼
const getReliabilityClass = (reliability: string) => {
  switch (reliability) {
    case '높음':
      return 'text-green-600';
    case '보통':
      return 'text-yellow-600';
    case '낮음':
      return 'text-red-600';
    case '알 수 없음':
      return 'text-gray-400';
    default:
      return 'text-gray-500';
  }
};
// ▲▲▲ [수정] ▲▲▲

export default function NewsCard({ news, index }: { news: NewsArticle, index: number }) {
  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
      <div className="relative w-full h-40 bg-gray-200 flex items-center justify-center">
        <span className="text-gray-400 text-sm">이미지 없음</span>
      </div>

      <div className="p-4 flex flex-col flex-grow">
        <span className="uppercase text-blue-600 font-semibold text-xs mb-1">
          {news.source}
        </span>

        <h3 className="font-bold text-lg mb-2 text-gray-800 line-clamp-2 h-14">
          {news.title}
        </h3>
        
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
          {news.summary}
        </p>

        <div className="text-right text-xs text-gray-500 mt-auto pt-2 border-t flex justify-between items-center">
          <span className={`font-bold ${getReliabilityClass(news.reliability)}`}>
            신뢰도: {news.reliability}
          </span>
          
          <time dateTime={news.date}>{formatDate(news.date)}</time>
        </div>
      </div>
    </article>
  );
}
