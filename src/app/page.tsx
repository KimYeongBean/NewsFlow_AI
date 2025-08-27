import NewsSection from '@/components/NewsSection';
import { NewsArticle, NewsCategory } from '@/types';
import fs from 'fs/promises';
import path from 'path';
import * as cheerio from 'cheerio';

async function getNewsFromHtmlFiles(): Promise<NewsArticle[]> {
  const newsDir = path.join(process.cwd(), 'public', 'news');
  const allNews: NewsArticle[] = [];
  // ▼▼▼ [수정] '알 수 없음'에 가장 낮은 정렬 순위(0)를 부여합니다. ▼▼▼
  const reliabilityOrder: Record<NewsArticle['reliability'], number> = {
    '높음': 3,
    '보통': 2,
    '낮음': 1,
    '알 수 없음': 0
  };
  // ▲▲▲ [수정] ▲▲▲

  try {
    const categoryDirs = await fs.readdir(newsDir);

    for (const category of categoryDirs) {
      const categoryPath = path.join(newsDir, category);
      const stats = await fs.stat(categoryPath);

      if (stats.isDirectory()) {
        const files = await fs.readdir(categoryPath);
        for (const file of files) {
          if (file.endsWith('.html')) {
            const filePath = path.join(categoryPath, file);
            const htmlContent = await fs.readFile(filePath, 'utf-8');
            const $ = cheerio.load(htmlContent);

            $('body h3').each((i, el) => {
              const titleElement = $(el).find('a');
              const infoElement = $(el).next('p');
              const summaryElement = infoElement.next('p.summary');

              const title = titleElement.text();
              const link = titleElement.attr('href') || '#';
              
              const infoText = infoElement.text();
              const sourceMatch = infoText.match(/언론사:\s*([^|]+)/);
              const dateMatch = infoText.match(/발행 시간:\s*(.*)/);
              
              const summaryHtml = summaryElement.html() || '';
              const reliabilitySpan = summaryElement.find('span.reliability').text();
              summaryElement.find('span.reliability').remove();
              const summary = summaryElement.text().replace('3줄 요약:', '').trim();

              // ▼▼▼ [수정] 신뢰도 파싱 로직 변경 ▼▼▼
              let reliabilityValue: NewsArticle['reliability'] = '알 수 없음'; // 기본값을 '알 수 없음'으로 설정
              const reliabilityMatch = reliabilitySpan.match(/신뢰도:\s*(높음|보통|낮음)/);
              if (reliabilityMatch) {
                reliabilityValue = reliabilityMatch[1].trim() as NewsArticle['reliability'];
              }
              // ▲▲▲ [수정] ▲▲▲

              // ▼▼▼ [수정] 신뢰도가 없어도 제목, 링크 등 기본 정보만 있으면 기사로 포함시킵니다. ▼▼▼
              if (title && link && sourceMatch && dateMatch) {
                const article: NewsArticle = {
                  category: category as NewsCategory,
                  title,
                  link,
                  source: sourceMatch[1].trim() as NewsArticle['source'],
                  date: dateMatch[1].trim(),
                  summary,
                  reliability: reliabilityValue,
                };
                allNews.push(article);
              }
              // ▲▲▲ [수정] ▲▲▲
            });
          }
        }
      }
    }
  } catch (error) {
    console.error("뉴스 데이터를 읽어오는 중 오류가 발생했습니다:", error);
    return [];
  }
  
  allNews.sort((a, b) => {
    const reliabilityDiff = reliabilityOrder[b.reliability] - reliabilityOrder[a.reliability];
    if (reliabilityDiff !== 0) {
      return reliabilityDiff;
    }
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });

  return allNews;
}

export default async function NewsHomepage() {
  const allNews = await getNewsFromHtmlFiles() || [];
  const breakingNews = allNews.slice(0, 4);

  return (
    <>
      <header className="bg-white py-4 flex items-center justify-between px-8 border-b">
        <h1 className="text-2xl font-extrabold text-blue-600">NEWS FLOW</h1>
        <div className="relative">
          <input type="text" placeholder="뉴스 검색..." className="border rounded-full py-2 px-4 w-64" />
          <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">
            🔍
          </button>
        </div>
      </header>
      
      <section className="bg-blue-800 text-white p-8">
        <h2 className="text-3xl font-bold mb-4 text-center">BREAKING NEWS</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {breakingNews.map(news => (
            <a 
              href={news.link}
              key={news.link}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-700 p-4 rounded-lg hover:bg-blue-600 transition-colors flex flex-col"
            >
              <span className="text-sm font-semibold bg-yellow-400 text-blue-900 px-2 py-1 rounded-full self-start mb-2">
                {news.category}
              </span>
              <h3 className="font-bold text-lg flex-grow">
                {news.title}
              </h3>
              <p className="text-xs text-blue-200 mt-2 self-end">
                {news.source}
              </p>
            </a>
          ))}
        </div>
      </section>

      <NewsSection allNews={allNews} />

      <footer className="bg-gray-800 py-6 px-8 text-center text-gray-400">
        <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row justify-between items-center">
            <ul className="flex space-x-6 mb-4 md:mb-0">
              <li><a href="#" className="hover:text-white">회사소개</a></li>
              <li><a href="#" className="hover:text-white">연락처</a></li>
              <li><a href="#" className="hover:text-white">개인정보보호정책</a></li>
            </ul>
            <div className="text-gray-500">
              © 2025 News Flow. All Rights Reserved.
            </div>
        </div>
      </footer>
    </>
  );
}
