"use client";

import { useRef, useState, MouseEvent } from 'react';
import { NewsArticle } from '@/types';
import { useLanguage } from '@/components/LanguageSelector';
import { useTranslation } from 'react-i18next';

interface FeaturedNewsProps {
  articles: NewsArticle[];
}

export default function FeaturedNews({ articles }: FeaturedNewsProps) {
  const { t } = useTranslation();
  const featuredArticles = articles.slice(0, 4);
  const { selectedLanguage } = useLanguage();
  const sliderRef = useRef<HTMLDivElement>(null);
  const [isDown, setIsDown] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    if (!sliderRef.current) return;
    setIsDown(true);
    sliderRef.current.classList.add('active:cursor-grabbing');
    setStartX(e.pageX - sliderRef.current.offsetLeft);
    setScrollLeft(sliderRef.current.scrollLeft);
  };

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!isDown || !sliderRef.current) return;
    e.preventDefault();
    const x = e.pageX - sliderRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    sliderRef.current.scrollLeft = scrollLeft - walk;
  };

  const handleMouseUpOrLeave = () => {
    if (!sliderRef.current) return;
    setIsDown(false);
    sliderRef.current.classList.remove('active:cursor-grabbing');
  };

  if (featuredArticles.length === 0) {
    return null;
  }

  return (
    <section className="py-12 bg-blue-400 border-b border-gray-200">
      <div className="container mx-auto px-4">
        {/* 타이틀 제거 (사용자 요청) */}
        <h2 className="sr-only">{t('featured_news')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredArticles.map((news, idx) => (
            <a key={`${news.link}-${idx}`} href={news.link} target="_blank" rel="noopener noreferrer" className="block bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden">
              <div className="relative w-full h-44">
                {news.imageUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={news.imageUrl} alt={news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']} className="w-full h-full object-cover" />
                ) : (
                  <div className="flex items-center justify-center w-full h-full bg-gray-200">
                    <span className="text-gray-500 text-sm">{t('no_image')}</span>
                  </div>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-bold text-md text-gray-800 line-clamp-2 h-12">{news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']}</h3>
                <p className="text-xs text-gray-500 mt-2">{news.source}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
