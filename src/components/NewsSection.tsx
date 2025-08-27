"use client";

import { useState } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle, Publisher, NewsCategory } from '@/types';

interface NewsSectionProps {
  allNews: NewsArticle[];
}

const CATEGORIES: NewsCategory[] = ['정치', '경제', '사회', 'IT_과학', '생활_문화', '세계'];
const PUBLISHERS: Publisher[] = [
  'MBC뉴스', '연합뉴스', '조선일보', '뉴스1', 'JTBC 뉴스',
  '중앙일보', 'SBS 뉴스', 'YTN', '한겨레', '경향신문',
  '오마이뉴스', '한국경제'
];

export default function NewsSection({ allNews }: NewsSectionProps) {
  const [selectedCategory, setSelectedCategory] = useState<NewsCategory>('경제');
  const [selectedPublisher, setSelectedPublisher] = useState<Publisher>('조선일보');

  const categoryFilteredNews = allNews.filter(news => news.category === selectedCategory);
  const publisherFilteredNews = allNews.filter(news => news.source === selectedPublisher);

  return (
    <>
      {/* --- 분야별 뉴스 섹션 --- */}
      <main className="bg-gray-50 pt-8 overflow-hidden">
        <nav className="bg-white py-3 border-b shadow-sm px-8">
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
        <section className="flex overflow-x-auto py-8 px-8 space-x-6 scrollbar-hide">
          {categoryFilteredNews.map((news, index) => (
            <div key={news.link} className="w-80 flex-shrink-0">
              <a href={news.link} target="_blank" rel="noopener noreferrer" className="block h-full">
                <NewsCard news={news} index={index} />
              </a>
            </div>
          ))}
        </section>
      </main>

      <hr className="border-gray-200" />

      {/* --- 언론사별 뉴스 섹션 --- */}
      <main className="bg-gray-50 pt-8 overflow-hidden">
        <section className="mb-8 px-8">
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
        
        <section className="flex overflow-x-auto py-8 px-8 space-x-6 scrollbar-hide">
          {publisherFilteredNews.map((news, index) => (
            <div key={news.link} className="w-80 flex-shrink-0">
              <a href={news.link} target="_blank" rel="noopener noreferrer" className="block h-full">
                <NewsCard news={news} index={index} />
              </a>
            </div>
          ))}
        </section>
      </main>
    </>
  );
}
