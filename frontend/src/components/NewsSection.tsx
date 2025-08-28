"use client";

import { useState, useEffect } from 'react';
import NewsCard from '@/components/NewsCard';
import { NewsArticle, Publisher, NewsCategory, CATEGORIES, CATEGORY_TRANSLATIONS } from '@/types';
import { useLanguage } from '@/components/LanguageSelector';
import { uiTexts } from '@/lib/i18n';
import { FaSearch } from 'react-icons/fa';

interface NewsSectionProps {
  allNews: NewsArticle[];
}

export default function NewsSection({ allNews }: NewsSectionProps) {
  const { selectedLanguage } = useLanguage();
  
  const [selectedCategory, setSelectedCategory] = useState<NewsCategory | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const categoryFilteredNews = selectedCategory === 'all'
    ? allNews
    : allNews.filter(news => news.category === selectedCategory);

  const uniquePublishers = [...new Set(categoryFilteredNews.map(news => news.source))];
  const [selectedPublisher, setSelectedPublisher] = useState<Publisher | 'all'>('all');

  useEffect(() => {
    setSelectedPublisher('all');
  }, [selectedCategory]);

  let filteredNews = categoryFilteredNews.filter(news =>
    selectedPublisher === 'all' || news.source === selectedPublisher
  );

  if (searchTerm) {
    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    filteredNews = filteredNews.filter(news => 
      (news.translatedTitles[selectedLanguage] || news.translatedTitles['ko'])
        .toLowerCase()
        .includes(lowerCaseSearchTerm) ||
      (news.translatedSummaries[selectedLanguage] || news.translatedSummaries['ko'])
        .toLowerCase()
        .includes(lowerCaseSearchTerm)
    );
  }

  const placeholderText: Record<string, string> = {
    ko: "뉴스 검색...",
    en: "Search news...",
    ja: "ニュース検索...",
    'zh-Hans': "搜索新闻...",
    fr: "Rechercher des nouvelles...",
  };

  return (
    <main className="bg-gray-50 overflow-hidden">
      {/* --- 분야별 뉴스 선택 UI (상단) --- */}
      <section className="px-8 sticky top-16 z-10 bg-gray-50 py-3 shadow-md">
        <div className="flex flex-col items-center gap-4">
          {/* 검색창 */}
          <div className="relative w-full max-w-2xl">
            <input
              type="text"
              placeholder={placeholderText[selectedLanguage] || "Search news..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full p-3 pl-5 pr-12 border border-gray-300 rounded-full focus:ring-blue-500 focus:border-blue-500 text-base"
            />
            <FaSearch className="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
          </div>

          <h2 className="text-2xl font-bold text-center">
            {uiTexts.newsByCategory[selectedLanguage]}
          </h2>

          <div className="flex justify-center flex-wrap gap-x-4 gap-y-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-full font-semibold transition-colors text-sm md:text-base ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
              }`}
            >
              {uiTexts.all[selectedLanguage]}
            </button>
            {(Object.keys(CATEGORIES) as NewsCategory[]).map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full font-semibold transition-colors text-sm md:text-base ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
                }`}
              >
                {CATEGORY_TRANSLATIONS[category][selectedLanguage]}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* --- 메인 콘텐츠 영역 (뉴스 그리드 + 언론사 목록) --- */}
      {/* ▼▼▼ [수정] pt-4를 pt-8로 늘려서 sticky 헤더와 겹치지 않도록 공간을 확보합니다. ▼▼▼ */}
      <div className="flex flex-col md:flex-row gap-12 pt-18 pb-8 px-8">
      {/* ▲▲▲ [수정] ▲▲▲ */}
        
        <section className="flex-grow grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
          {filteredNews.map((news, index) => (
            <NewsCard
              key={news.link + index}
              link={news.link}
              title={news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']}
              source={news.source}
              date={news.date}
              summary={news.translatedSummaries[selectedLanguage] || news.translatedSummaries['ko']}
              reliability={news.reliability}
              imageUrl={news.imageUrl}
            />
          ))}
        </section>

        <aside className="w-full md:w-32 flex-shrink-0">
          <h2 className="text-xl font-bold mb-4 text-center md:text-left">{uiTexts.newsByPublisher[selectedLanguage]}</h2>
          
          <div className="flex flex-row md:flex-col flex-wrap md:flex-nowrap gap-2">
            <button
              onClick={() => setSelectedPublisher('all')}
              className={`w-full text-left p-2 rounded-md font-semibold transition-colors text-sm ${
                selectedPublisher === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 shadow-sm'
              }`}
            >
              {uiTexts.all[selectedLanguage]}
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
