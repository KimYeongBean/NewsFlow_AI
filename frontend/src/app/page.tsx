'use client';

import { useState, useEffect } from 'react';
import { NewsArticle } from '@/types';
import { useTranslation } from 'react-i18next';

// 컴포넌트 import
import NewsSection from '@/components/NewsSection';
import FeaturedNews from '@/components/FeaturedNews';
import LanguageSelector from '@/components/LanguageSelector';
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
  const { t } = useTranslation();
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
    <div className="container mx-auto">
      <header className="text-center py-6 bg-white">
        <h1 className="text-4xl font-extrabold text-gray-800">NewsFlow AI</h1>
        <p className="text-lg text-gray-500 mt-2">{t('subtitle')}</p>
      </header>

      <LanguageSelector />

      {/* 검색바는 아래(주요뉴스 아래)에 위치하도록 변경됨 */}

      {isLoading ? (
        <div className="text-center py-20">
          <p className="text-xl text-gray-500">{t('loading')}</p>
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
              <p className="text-xl text-gray-500">{t('no_news')}</p>
              <p className="text-md text-gray-400 mt-2">{t('no_news_description')}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
