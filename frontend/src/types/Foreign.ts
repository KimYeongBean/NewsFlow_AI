import { LanguageCode } from '@/types';

export const uiTexts: Record<string, Record<LanguageCode, string>> = {
  // Header in page.tsx
  // LanguageSelector.tsx

  // NewsSection.tsx
  newsByCategory: {
    ko: '분야별 뉴스',
    en: 'Category',
    ja: '分野別ニュース',
    'zh-Hans': '按类别分类的新闻',
    fr: 'Actualités par catégorie',
  },
  newsByPublisher: {
    ko: '언론사별',
    en: 'Publisher',
    ja: 'メディア別',
    'zh-Hans': '按出版社',
    fr: 'Par éditeur',
  },
  all: {
    ko: '전체',
    en: 'All',
    ja: 'すべて',
    'zh-Hans': '全部',
    fr: 'Tout',
  }
};