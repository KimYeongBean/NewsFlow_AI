import { Reliability, Publisher } from '@/types';

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

// 신뢰도에 따른 '배경색' CSS 클래스를 반환하는 함수
const getReliabilityBgClass = (reliability: Reliability) => {
  switch (reliability) {
    case '높음':
      return 'bg-green-600';
    case '보통':
      return 'bg-yellow-600';
    case '낮음':
      return 'bg-red-600';
    case '알 수 없음':
      return 'bg-gray-400';
    default:
      return 'bg-gray-500';
  }
};

// NewsCard가 받을 props 타입을 정의
interface NewsCardProps {
  link: string;
  title: string;
  source: Publisher;
  date: string;
  summary: string;
  reliability: Reliability;
  imageUrl?: string;
}

export default function NewsCard({ link, title, source, date, summary, reliability, imageUrl }: NewsCardProps) {
  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
      {/* ▼▼▼ [수정] 날짜를 제거하고 신뢰도만 표시하도록 변경합니다. ▼▼▼ */}
      <div className={`flex justify-start items-center text-xs px-4 py-3 text-white rounded-t-lg ${getReliabilityBgClass(reliability)}`}>
        <span className="font-bold">
          신뢰도: {reliability}
        </span>
      </div>
      {/* ▲▲▲ [수정] ▲▲▲ */}

      <div className="relative w-full h-40 bg-gray-200 flex items-center justify-center">
        {imageUrl ? (
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

        {/* ▼▼▼ [수정] 날짜를 카드 하단에 새로 추가하고 font-bold를 적용합니다. ▼▼▼ */}
        <div className="mt-auto pt-2 border-t text-right text-xs text-black-500">
            <time dateTime={date} className="font-bold">{formatDate(date)}</time>
        </div>
        {/* ▲▲▲ [수정] ▲▲▲ */}
      </div>
    </article>
  );
}
