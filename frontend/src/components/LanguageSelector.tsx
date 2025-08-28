"use client";

import { createContext, useState, useContext, ReactNode } from 'react';
import { LanguageCode } from '@/types';

// --- Context Definition ---

// 지원하는 언어와 표시될 이름
const SUPPORTED_LANGUAGES: { code: LanguageCode; name: string }[] = [
  { code: 'ko', name: '한국어' },
  { code: 'en', name: 'English' },
  { code: 'ja', name: '日本語' },
  { code: 'zh-Hans', name: '中文(简体)' },
  { code: 'fr', name: 'Français' },
];

interface LanguageContextType {
  selectedLanguage: LanguageCode;
  setSelectedLanguage: (language: LanguageCode) => void;
  supportedLanguages: typeof SUPPORTED_LANGUAGES;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// --- Context Provider ---

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [selectedLanguage, setSelectedLanguage] = useState<LanguageCode>('ko');

  const value = {
    selectedLanguage,
    setSelectedLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

// --- Custom Hook ---

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// --- UI Component ---

export default function LanguageSelector() {
  const { selectedLanguage, setSelectedLanguage, supportedLanguages } = useLanguage();

  return (
    <section className="bg-white py-4 border-b shadow-sm sticky top-0 z-10">
      <div className="flex justify-center items-center space-x-4">
        <span className="font-semibold text-gray-700">언어 선택:</span>
        {supportedLanguages.map(({ code, name }) => (
          <button
            key={code}
            onClick={() => setSelectedLanguage(code)}
            className={`px-3 py-1 text-sm rounded-full font-semibold transition-colors ${
              selectedLanguage === code
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {name}
          </button>
        ))}
      </div>
    </section>
  );
}
