'use client';

import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';

// 컴포넌트 import
import NewsSection from '@/components/NewsSection';
import FeaturedNews from '@/components/FeaturedNews';
import LanguageSelector, { LanguageProvider } from '@/components/LanguageSelector';
import Search from '@/components/Search'; // Search 컴포넌트 import

/**
 * 백엔드 API에서 뉴스 데이터를 가져오는 함수
 */
async function getNewsFromApi(): Promise<NewsArticle[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  try {
    const res = await fetch(`${apiUrl}/api/news`, { cache: 'no-store' });

    if (!res.ok) {
      console.error(`API 호출 실패: ${res.status} ${res.statusText}`);
      return [];
    }

    const data: NewsArticle[] = await res.json();
    data.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return data;

  } catch (error) {
    console.error("뉴스 데이터 fetch 중 네트워크 또는 기타 오류 발생:", error);
    return [];
  }
}

export default function HomePage() {
  const [allNews, setAllNews] = useState<NewsArticle[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadNews() {
      setIsLoading(true);
      const newsData = await getNewsFromApi();
      // 백엔드가 translatedTitles를 제공하지 않는 경우도 대비하여 기본화
      const normalized = newsData.map(n => ({
        ...n,
        translatedTitles: n.translatedTitles || { ko: n.summary || '', en: n.summary || '', ja: n.summary || '', fr: n.summary || '', 'zh-Hans': n.summary || '' },
        translatedSummaries: n.translatedSummaries || { ko: n.summary || '', en: n.summary || '', ja: n.summary || '', fr: n.summary || '', 'zh-Hans': n.summary || '' },
      }));
      setAllNews(normalized);
      setIsLoading(false);
    }
    loadNews();
  }, []);

  const filteredNews = allNews.filter(news =>
    Object.values(news.translatedTitles).some(title =>
      title.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <LanguageProvider>
      <div className="container mx-auto">
        <header className="text-center py-6 bg-white">
          <h1 className="text-4xl font-extrabold text-gray-800">NewsFlow AI</h1>
          <p className="text-lg text-gray-500 mt-2">AI와 함께하는 스마트한 뉴스 소비</p>
        </header>

        <LanguageSelector />

        {/* 검색바는 아래(주요뉴스 아래)에 위치하도록 변경됨 */}

        {isLoading ? (
          <div className="text-center py-20">
            <p className="text-xl text-gray-500">뉴스를 불러오는 중입니다...</p>
          </div>
        ) : (
          <>
            {/* FeaturedNews는 상단에 위치 */}
            <FeaturedNews articles={filteredNews} />

            {/* 검색바를 주요뉴스 바로 아래에 배치: 아래 배경과 통일하고 바로 붙도록 조정 */}
            <div className="w-full bg-gray-50 py-6 mt-0 -mt-6">
              <div className="max-w-3xl mx-auto">
                <div className="p-2">
                  <Search value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                </div>
              </div>
            </div>
            {filteredNews.length > 0 ? (
              <NewsSection allNews={filteredNews} />
            ) : (
              <div className="text-center py-20">
                <p className="text-xl text-gray-500">표시할 뉴스가 없습니다.</p>
                <p className="text-md text-gray-400 mt-2">백엔드 서버가 실행 중인지, 또는 뉴스 데이터가 정상적으로 수집되었는지 확인해주세요.</p>
              </div>
            )}
          </>
        )}
      </div>
    </LanguageProvider>
  );
}
