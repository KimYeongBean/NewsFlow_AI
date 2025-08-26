import Image from 'next/image';
import { NewsArticle } from '@/types';

// 날짜 형식을 'YYYY.MM.DD HH:mm'으로 변환하는 함수
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}.${month}.${day} ${hours}:${minutes}`;
};


export default function NewsCard({ news }: { news: NewsArticle }) {
  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 h-full flex flex-col">
      <div className="relative w-full h-40">
        {/* 이미지 내용 */}
        <Image
          src={news.imageSrc}
          alt={news.title}
          fill
          style={{ objectFit: 'cover' }}
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          priority={news.id <= 4}
        />
      </div>

      <div className="p-4 flex flex-col flex-grow">
        <span className="uppercase text-blue-600 font-semibold text-xs mb-1">
          {news.publisher}
        </span>

        {/* 제목(h3)에 고정 높이(h-14)를 추가하여 레이아웃이 변하지 않도록 합니다. */}
        <h3 className="font-bold text-lg mb-2 text-gray-800 line-clamp-2 h-14">
          {news.title}
        </h3>
        
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
          {news.description}
        </p>

        <div className="text-right text-xs text-gray-500 mt-auto pt-2 border-t">
          <time dateTime={news.publishedDate}>{formatDate(news.publishedDate)}</time>
        </div>
      </div>
    </article>
  );
}