import Image from 'next/image';

// 데이터 타입 정의
type NewsArticle = {
  id: number;
  imageSrc: string;
  publisher: string;
  title: string;
  description: string;
  link: string;
  publishedDate: string;
};

// 날짜 포맷팅 함수
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
      {/* 이미지 영역 */}
      <div className="relative w-full h-40">
        <Image
          src={news.imageSrc}
          alt={news.title}
          fill
          style={{ objectFit: 'cover' }}
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          priority={news.id <= 4}
        />
      </div>

      {/* 텍스트 콘텐츠 영역 */}
      <div className="p-4 flex flex-col flex-grow">
        {/* 1. 기존 UI의 파란색 언론사명 스타일을 여기에 다시 추가합니다. */}
        <span className="uppercase text-blue-600 font-semibold text-xs mb-1">
          {news.publisher}
        </span>

        <h3 className="font-bold text-lg mb-2 text-gray-800 line-clamp-2">
          {news.title}
        </h3>
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
          {news.description}
        </p>

        {/* 2. 하단에는 발행 시간만 깔끔하게 표시합니다. */}
        <div className="text-right text-xs text-gray-500 mt-auto pt-2 border-t">
          <time dateTime={news.publishedDate}>{formatDate(news.publishedDate)}</time>
        </div>
      </div>
    </article>
  );
}