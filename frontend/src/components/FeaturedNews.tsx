"use client";

import { useRef, useState, MouseEvent } from 'react';
import { NewsArticle } from '@/types';
import { useLanguage } from '@/components/LanguageSelector'; // 경로 수정

interface FeaturedNewsProps {
  articles: NewsArticle[];
}

export default function FeaturedNews({ articles }: FeaturedNewsProps) {
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
    <section className="py-10 bg-blue-400 border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div
          ref={sliderRef}
          className="flex flex-nowrap space-x-6 overflow-x-auto cursor-grab select-none scrollbar-hide -mx-4 px-22"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUpOrLeave}
          onMouseLeave={handleMouseUpOrLeave}
        >
          {featuredArticles.map((news) => (
            <a
              key={news.link}
              href={news.link}
              target="_blank"
              rel="noopener noreferrer"
              className="block flex-shrink-0 w-80 bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300"
              onClick={(e) => {
                if (sliderRef.current && Math.abs(sliderRef.current.scrollLeft - scrollLeft) > 5) {
                  e.preventDefault();
                }
              }}
            >
              <div className="relative w-full h-40 bg-gray-200">
                {news.imageUrl ? (
                  <img src={news.imageUrl} alt={news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']} className="w-full h-full object-cover" />
                ) : (
                  <div className="flex items-center justify-center w-full h-full">
                    <span className="text-gray-500 text-sm">이미지 없음</span>
                  </div>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-bold text-md text-gray-800 line-clamp-2 h-12">
                  {news.translatedTitles[selectedLanguage] || news.translatedTitles['ko']}
                </h3>
                <p className="text-xs text-gray-500 mt-2">{news.source}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
