"use client";

import { useState, useEffect } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle, Publisher, NewsCategory, CATEGORIES } from '@/types';
import { useLanguage } from '@/components/LanguageSelector';
import { useTranslation } from 'react-i18next';

interface NewsSectionProps {
  allNews: NewsArticle[];
}

export default function NewsSection({ allNews }: NewsSectionProps) {
  const { t } = useTranslation();
  const { selectedLanguage } = useLanguage();
  
  const [selectedCategory, setSelectedCategory] = useState<NewsCategory | 'all'>('all');

  const categoryFilteredNews = selectedCategory === 'all'
    ? allNews
    : allNews.filter(news => news.category === selectedCategory);

  const uniquePublishers = [...new Set(categoryFilteredNews.map(news => news.source))];
  const [selectedPublisher, setSelectedPublisher] = useState<string | 'all'>('all');

  useEffect(() => {
    setSelectedPublisher('all');
  }, [selectedCategory]);

  const filteredNews = categoryFilteredNews.filter(news =>
    selectedPublisher === 'all' || news.source === selectedPublisher
  );

  return (
    <main className="bg-gray-50 pt-8 overflow-hidden">
      {/* --- 분야별 뉴스 선택 UI (상단) --- */}
      
      <section className="mb-8 px-8">
        <h2 className="text-2xl font-bold mb-4 text-center text-black">{t('news_by_category')}</h2>
        <div className="flex justify-center flex-wrap gap-x-4 gap-y-2">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-4 py-2 rounded-full font-semibold transition-colors text-sm md:text-base ${
              selectedCategory === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
            }`}
          >
            {t('all')}
          </button>
          {(Object.keys(CATEGORIES) as NewsCategory[]).filter(c => c !== '전체').map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full font-semibold transition-colors text-sm md:text-base ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      {/* --- 메인 콘텐츠 영역 (뉴스 그리드 + 언론사 목록) --- */}
      <div className="flex flex-col md:flex-row gap-12 p-8">
        
        {/* --- 최종 필터링된 뉴스 목록 (왼쪽) --- */}
        <section className="flex-grow grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
          {filteredNews.map((news, index) => (
            <NewsCard
              key={news.link + index}
              link={news.link}
              title={news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']}
              source={news.source}
              date={news.date}
              summary={news.summary}
              reliability={news.reliability}
              imageUrl={news.imageUrl}
            />
          ))}
        </section>

        {/* --- 언론사별 선택 UI (오른쪽 세로 목록) --- */}
        <aside className="w-full md:w-32 flex-shrink-0">
          <h2 className="text-xl font-bold mb-4 text-center md:text-left text-black">{t('by_publisher')}</h2>
          <div className="flex flex-row md:flex-col flex-wrap md:flex-nowrap gap-2">
            <button
              onClick={() => setSelectedPublisher('all')}
              className={`w-full text-left p-2 rounded-md font-semibold transition-colors text-sm ${
                selectedPublisher === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
              }`}
            >
              {t('all')}
            </button>
            {uniquePublishers.map(publisher => (
              <button
                key={publisher}
                onClick={() => setSelectedPublisher(publisher)}
                className={`w-full text-left p-2 rounded-md font-semibold transition-colors text-sm ${
                  selectedPublisher === publisher
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
                }`}
              >
                {publisher}
              </button>
            ))}
          </div>
        </aside>

      </div>
    </main>
  );
}
