"use client";

import { useState, useEffect } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle } from '@/types';

// 백엔드 API로부터 받은 데이터 타입
interface ApiResponse {
  category: string;
  sub_category: string;
  articles: NewsArticle[];
}

const CATEGORIES: NewsArticle['category'][] = ['정치', '경제', '사회', 'IT/기술', '생활_문화', '세계'];
const TRUSTED_SOURCES = ["조선일보", "한겨레", "중앙일보", "동아일보", "경향신문"]; // 신뢰도 평가 기준 언론사

export default function NewsSection() {
  const [selectedCategory, setSelectedCategory] = useState<NewsArticle['category']>('정치');
  const [newsData, setNewsData] = useState<ApiResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNews = async () => {
      setIsLoading(true);
      setError(null);
      setNewsData([]); // 카테고리 변경 시 기존 데이터 초기화

      try {
        const response = await fetch(`http://127.0.0.1:8000/api/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            categories: [selectedCategory],
            trusted_sources: TRUSTED_SOURCES,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '뉴스 데이터를 불러오는 데 실패했습니다.');
        }

        const data: ApiResponse[] = await response.json();
        setNewsData(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, [selectedCategory]); // selectedCategory가 변경될 때마다 API 호출

  return (
    <main className="bg-gray-50 pt-8 pb-12">
      <nav className="bg-white py-3 border-b shadow-sm px-8 sticky top-0 z-10">
        <ul className="flex justify-center space-x-8 font-semibold">
          {CATEGORIES.map(category => (
            <li key={category}>
              <button
                onClick={() => setSelectedCategory(category)}
                className={`pb-1 hover:text-blue-600 transition-colors duration-200 ${
                  selectedCategory === category
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600'
                }`}
              >
                {category.replace('_', '/')}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="px-8 mt-8">
        {isLoading ? (
          <div className="text-center py-20">
            <p className="text-lg font-semibold text-gray-600">AI가 뉴스를 분석하고 있습니다...</p>
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-lg font-semibold text-red-600">오류: {error}</p>
          </div>
        ) : (
          newsData.map((section, index) => (
            <section key={index} className="mb-12">
              <h2 className="text-2xl font-bold mb-4 text-gray-800 border-l-4 border-blue-600 pl-3">
                {section.sub_category}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {section.articles.map((news, newsIndex) => (
                  <NewsCard key={newsIndex} news={news} />
                ))}
              </div>
            </section>
          ))
        )}
      </div>
    </main>
  );
}