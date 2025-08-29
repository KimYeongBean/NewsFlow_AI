import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import translationEN from './locales/en/translation.json';
import translationKO from './locales/ko/translation.json';
import translationJA from './locales/ja/translation.json';
import translationZH from './locales/zh-Hans/translation.json';
import translationFR from './locales/fr/translation.json';

const resources = {
  en: {
    translation: translationEN,
  },
  ko: {
    translation: translationKO,
  },
  ja: {
    translation: translationJA,
  },
  'zh-Hans': {
    translation: translationZH,
  },
  fr: {
    translation: translationFR,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ko', // 기본 언어
    interpolation: {
      escapeValue: false, // React already does escaping
    },
  });

export default i18n;