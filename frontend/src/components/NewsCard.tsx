import { Reliability } from '@/types';

// 날짜 포맷 함수
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}.${month}.${day} ${hours}:${minutes}`;
};

// 신뢰도에 따른 CSS 클래스를 반환하는 함수
const getReliabilityClass = (reliability: Reliability) => {
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

// NewsCard가 받을 props 타입을 정의
interface NewsCardProps {
  link: string;
  title: string;
  source: string;
  date: string;
  summary: string;
  reliability: Reliability;
  imageUrl?: string;
}

export default function NewsCard({ link, title, source, date, summary, reliability, imageUrl }: NewsCardProps) {
  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
      <div className={`flex justify-start items-center text-xs px-4 py-3 text-white rounded-t-lg ${getReliabilityClass(reliability)}`}>
        <span className="font-bold">
          신뢰도: {reliability}
        </span>
      </div>

      <div className="relative w-full h-40 bg-gray-200 flex items-center justify-center">
        {imageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={imageUrl} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="flex items-center justify-center w-full h-full">
            <span className="text-gray-400 text-sm">이미지 없음</span>
          </div>
        )}
      </div>

      <div className="p-4 flex flex-col flex-grow">
        <span className="uppercase text-blue-600 font-semibold text-xs mb-1">
          {source}
        </span>
        
        <a href={link} target="_blank" rel="noopener noreferrer">
            <h3 className="font-bold text-lg mb-2 text-gray-800 line-clamp-2 h-14 hover:underline">
              {title}
            </h3>
        </a>
        
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
          {summary}
        </p>

        <div className="mt-auto pt-2 border-t text-right text-xs text-black-500">
            <time dateTime={date} className="font-bold">{formatDate(date)}</time>
        </div>
      </div>
    </article>
  );
}
