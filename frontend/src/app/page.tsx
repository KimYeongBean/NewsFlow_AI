import fs from 'fs/promises';
import path from 'path';
import * as cheerio from 'cheerio';
import { NewsArticle, LanguageCode, Reliability, Publisher, NewsCategory, NewsSubCategory } from '@/types';

// 컴포넌트 import
import NewsSection from '@/components/NewsSection';
import FeaturedNews from '@/components/FeaturedNews';
import LanguageSelector, { LanguageProvider } from '@/components/LanguageSelector';

/**
 * public/news 폴더 전체를 스캔하여 모든 HTML 파일을 파싱하는 함수
 */
async function getNewsFromHtml(): Promise<NewsArticle[]> {
  const newsBaseDir = path.join(process.cwd(), 'public', 'news');
  const allArticles: NewsArticle[] = [];

  try {
    const categoryDirs = await fs.readdir(newsBaseDir, { withFileTypes: true });

    for (const categoryDir of categoryDirs) {
      if (categoryDir.isDirectory()) {
        const category = categoryDir.name as NewsCategory;
        const categoryPath = path.join(newsBaseDir, category);
        const files = await fs.readdir(categoryPath);

        for (const file of files) {
          if (path.extname(file) === '.html') {
            const subCategory = path.basename(file, '_news.html').replace(/_/g, '/') as NewsSubCategory;
            const filePath = path.join(categoryPath, file);
            const htmlContent = await fs.readFile(filePath, 'utf-8');
            const $ = cheerio.load(htmlContent);

            $('.article-block').each((_, element) => {
              const headerText = $(element).find('p > b').parent().text();
              const sourceMatch = headerText.match(/언론사:\s*(.*?)\s*\|/);
              const dateMatch = headerText.match(/발행 시간:\s*(.*)/);

              const source = sourceMatch ? sourceMatch[1].trim() as Publisher : '알 수 없음';
              const dateString = dateMatch ? dateMatch[1].trim() : new Date().toISOString();
              const formattedDateString = dateString.replace(/(\d{4})\.(\d{2})\.(\d{2})\s(\d{2}):(\d{2})/, '$1-$2-$3T$4:$5:00');
              const date = new Date(formattedDateString).toISOString();

              const link = $(element).find('h3 a').attr('href') || '#';
              const imageUrl = $(element).find('.article-image').attr('src');
              const summaryElement = $(element).find('.content.ko .summary');
              const reliabilitySpan = summaryElement.find('.reliability').clone();
              summaryElement.find('.reliability').remove();
              const summary = summaryElement.text().trim() || "요약 정보 없음";
              
              const reliabilityMatch = reliabilitySpan.text().match(/신뢰도:\s*(.*)/);
              const reliability = reliabilityMatch ? reliabilityMatch[1].trim() as Reliability : '알 수 없음';
              
              // ▼▼▼ [수정] 모든 언어의 제목을 올바르게 추출하도록 로직을 변경합니다. ▼▼▼
              const translatedTitles = {} as Record<LanguageCode, string>;
              $(element).find('.content').each((_, contentEl) => {
                const classList = $(contentEl).attr('class')?.split(' ') || [];
                // 클래스 리스트에서 언어 코드를 찾습니다. (예: 'ko', 'en', 'ja')
                const lang = classList.find(c => c !== 'content' && c !== 'active') as LanguageCode;
                if (lang) {
                  // 각 언어 블록('.content') 내부의 h3 태그에서 제목을 직접 가져옵니다.
                  const title = $(contentEl).find('h3 a').text().trim();
                  if (title) {
                    translatedTitles[lang] = title;
                  }
                }
              });
              // ▲▲▲ [수정] ▲▲▲
              
              allArticles.push({
                category,
                subCategory,
                link,
                source,
                date,
                summary,
                reliability,
                translatedTitles,
                imageUrl: imageUrl || undefined, // 추출한 이미지 URL 추가
                evaluation: ''
              });
            });
          }
        }
      }
    }
    allArticles.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return allArticles;
  } catch (error) {
    console.error("HTML 파일 처리 중 오류 발생:", error);
    return [];
  }
}

export default async function HomePage() {
  const allNews = await getNewsFromHtml();

  return (
    <LanguageProvider>
      <div className="container mx-auto">
        <header className="text-center py-10 bg-white">
          <h1 className="text-4xl font-extrabold text-gray-800">NewsFlow AI</h1>
          <p className="text-lg text-gray-500 mt-2">AI와 함께하는 스마트한 뉴스 소비</p>
        </header>

        <LanguageSelector />
        
        <FeaturedNews articles={allNews} />

        {allNews.length > 0 ? (
          <NewsSection allNews={allNews} />
        ) : (
          <div className="text-center py-20">
            <p className="text-xl text-gray-500">표시할 뉴스가 없습니다.</p>
            <p className="text-md text-gray-400 mt-2">`newsaidi.py`를 실행하여 `public/news/` 폴더에 HTML 파일들을 생성했는지 확인해주세요.</p>
          </div>
        )}
      </div>
    </LanguageProvider>
  );
}
