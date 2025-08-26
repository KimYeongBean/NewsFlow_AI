"use client";

import { useState } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle, Publisher } from '@/types';

interface NewsSectionProps {
  allNews: NewsArticle[];
}

const CATEGORIES: NewsArticle['category'][] = ['경제', '사회', '정치', 'IT/기술', '문화', '세계'];
const PUBLISHERS: Publisher[] = ['KBS', 'MBC', 'SBS', '헤럴드경제', '한겨레'];

export default function NewsSection({ allNews }: NewsSectionProps) {
  const [selectedCategory, setSelectedCategory] = useState<NewsArticle['category']>('경제');
  const [selectedPublisher, setSelectedPublisher] = useState<Publisher>('KBS');

  const categoryFilteredNews = allNews.filter(news => news.category === selectedCategory);
  const publisherFilteredNews = allNews.filter(news => news.publisher === selectedPublisher);

  return (
    <>
      {/* --- 분야별 뉴스 섹션 --- */}
      <main className="bg-gray-50 pt-8 overflow-hidden"> {/* ✅ STEP 1: overflow-hidden 추가 */}
        <nav className="bg-white py-3 border-b shadow-sm px-8"> {/* px-8 추가 */}
          <ul className="flex justify-center space-x-8 font-semibold">
            {CATEGORIES.map(category => (
              <li key={category}>
                <button
                  onClick={() => setSelectedCategory(category)}
                  className={`pb-1 hover:text-blue-600 ${selectedCategory === category
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600'
                    }`}
                >
                  {category}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        {/* ✅ STEP 2: 기존 grid를 flex 기반의 가로 스크롤 컨테이너로 변경 */}
        <section className="flex overflow-x-auto py-8 px-8 space-x-6 scrollbar-hide">
          {categoryFilteredNews.map((news) => (
            // ✅ STEP 3: 각 뉴스 카드의 너비를 고정하고, 줄어들지 않도록 설정
            <div key={news.id} className="w-80 flex-shrink-0">
              <a href={news.link} target="_blank" rel="noopener noreferrer" className="block h-full">
                <NewsCard news={news} />
              </a>
            </div>
          ))}
        </section>
      </main>

      <hr className="border-gray-200" />

      {/* --- 언론사별 뉴스 섹션 --- */}
      <main className="bg-gray-50 pt-8 overflow-hidden"> {/* ✅ STEP 1: overflow-hidden 추가 */}
        <section className="mb-8 px-8"> {/* px-8 추가 */}
          <h2 className="text-2xl font-bold mb-4 text-center">언론사별 뉴스</h2>
          <div className="flex justify-center space-x-4">
            {PUBLISHERS.map(publisher => (
              <button
                key={publisher}
                onClick={() => setSelectedPublisher(publisher)}
                className={`px-4 py-2 rounded-full font-semibold transition-colors ${
                  selectedPublisher === publisher
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
                }`}
              >
                {publisher}
              </button>
            ))}
          </div>
        </section>
        
        {/* ✅ STEP 2: 여기도 동일하게 가로 스크롤 컨테이너로 변경 */}
        <section className="flex overflow-x-auto py-8 px-8 space-x-6 scrollbar-hide">
          {publisherFilteredNews.map((news) => (
            // ✅ STEP 3: 각 뉴스 카드의 너비를 고정하고, 줄어들지 않도록 설정
            <div key={news.id} className="w-80 flex-shrink-0">
              <a href={news.link} target="_blank" rel="noopener noreferrer" className="block h-full">
                <NewsCard news={news} />
              </a>
            </div>
          ))}
        </section>
      </main>
    </>
  );
}