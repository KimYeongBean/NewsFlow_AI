import { NewsArticle } from '@/types';

// 컴포넌트 import
import NewsSection from '@/components/NewsSection';
import FeaturedNews from '@/components/FeaturedNews';
import LanguageSelector, { LanguageProvider } from '@/components/LanguageSelector';

/**
 * 백엔드 API에서 뉴스 데이터를 가져오는 함수
 */
async function getNewsFromApi(): Promise<NewsArticle[]> {
  // 환경 변수에서 백엔드 API URL을 가져옵니다.
  // 로컬 개발 시에는 .env.local 파일에 NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 와 같이 설정합니다.
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    console.error("오류: NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다.");
    // 환경 변수가 없을 경우 빈 배열을 반환하여 페이지가 깨지는 것을 방지합니다.
    return [];
  }

  try {
    // Next.js 13+의 확장된 fetch를 사용하여 데이터를 가져오고 캐싱합니다.
    // { next: { revalidate: 600 } }는 10분(600초)마다 데이터를 새로고침하도록 설정합니다.
    const res = await fetch(`${apiUrl}/api/news`, { next: { revalidate: 600 } });

    if (!res.ok) {
      // API 응답이 실패했을 경우 에러를 기록하고 빈 배열을 반환합니다.
      console.error(`API 호출 실패: ${res.status} ${res.statusText}`);
      return [];
    }

    const data: NewsArticle[] = await res.json();
    // 날짜 순으로 정렬 (API에서 이미 정렬했지만, 한 번 더 확인)
    data.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return data;

  } catch (error) {
    console.error("뉴스 데이터 fetch 중 네트워크 또는 기타 오류 발생:", error);
    // 네트워크 오류 등이 발생했을 경우 빈 배열을 반환합니다.
    return [];
  }
}

export default async function HomePage() {
  const allNews = await getNewsFromApi();

  return (
    <LanguageProvider>
      <div className="container mx-auto">
        <header className="text-center py-10 bg-white">
          <h1 className="text-4xl font-extrabold text-gray-800">NewsFlow AI</h1>
          <p className="text-lg text-gray-500 mt-2">AI와 함께하는 스마트한 뉴스 소비</p>
        </header>

        <LanguageSelector />
        
        <FeaturedNews articles={allNews} />

        {allNews.length > 0 ? (
          <NewsSection allNews={allNews} />
        ) : (
          <div className="text-center py-20">
            <p className="text-xl text-gray-500">표시할 뉴스가 없습니다.</p>
            <p className="text-md text-gray-400 mt-2">백엔드 서버가 실행 중인지, 또는 뉴스 데이터가 정상적으로 수집되었는지 확인해주세요.</p>
          </div>
        )}
      </div>
    </LanguageProvider>
  );
}
