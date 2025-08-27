"use client";

import { useState } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle, Publisher } from '@/types';
import { useLanguage } from '@/components/LanguageSelector'; // 경로 수정

interface NewsSectionProps {
  allNews: NewsArticle[];
}

export default function NewsSection({ allNews }: NewsSectionProps) {
  const { selectedLanguage } = useLanguage();
  const uniquePublishers = [...new Set(allNews.map(news => news.source))];
  const [selectedPublisher, setSelectedPublisher] = useState<Publisher | 'all'>(uniquePublishers[0] || 'all');

  const filteredNews = allNews.filter(news =>
    selectedPublisher === 'all' || news.source === selectedPublisher
  );

  return (
    <>
      <main className="bg-gray-50 pt-8 overflow-hidden">
        <section className="mb-8 px-8">
          <h2 className="text-2xl font-bold mb-4 text-center">언론사별 뉴스</h2>
          <div className="flex justify-center flex-wrap gap-2">
            <button
              onClick={() => setSelectedPublisher('all')}
              className={`px-4 py-2 rounded-full font-semibold transition-colors ${
                selectedPublisher === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
              }`}
            >
              전체
            </button>
            {uniquePublishers.map(publisher => (
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

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-8">
          {filteredNews.map((news, index) => (
            <NewsCard
              key={news.link + index}
              link={news.link}
              title={news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']}
              source={news.source}
              date={news.date}
              summary={news.summary}
              reliability={news.reliability}
            />
          ))}
        </section>
      </main>
    </>
  );
}
