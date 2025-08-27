import { NewsArticle } from '@/types';

// 신뢰도 등급에 따른 색상 클래스를 반환하는 함수
const getReliabilityClass = (reliabilityClass: string) => {
  switch (reliabilityClass) {
    case 'high':
      return 'bg-blue-100 text-blue-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// 날짜 형식을 'YYYY.MM.DD HH:mm'으로 변환하는 함수
const formatDate = (dateString: string) => {
  if (!dateString) return '날짜 정보 없음';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '유효하지 않은 날짜';
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}.${month}.${day} ${hours}:${minutes}`;
};

export default function NewsCard({ news }: { news: NewsArticle }) {
  return (
    <a href={news.link} target="_blank" rel="noopener noreferrer" className="block h-full">
      <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
        <div className="p-4 flex flex-col flex-grow">
          <div className="flex justify-between items-start mb-2">
            <span className="font-semibold text-sm text-gray-700">
              {news.source}
            </span>
            <span
              className={`px-2 py-1 text-xs font-bold rounded-full ${getReliabilityClass(news.reliability_class)}`}
            >
              신뢰도: {news.reliability}
            </span>
          </div>

          <h3 className="font-bold text-md mb-2 text-gray-900 line-clamp-2 h-12">
            {news.title}
          </h3>
          
          <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
            {news.summary}
          </p>

          <div className="text-right text-xs text-gray-500 mt-auto pt-2 border-t">
            <time dateTime={news.date}>{formatDate(news.date)}</time>
          </div>
        </div>
      </article>
    </a>
  );
}