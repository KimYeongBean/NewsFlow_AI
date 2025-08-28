"use client";

import { FaSearch } from 'react-icons/fa';

interface SearchProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function Search({ value, onChange }: SearchProps) {
  return (
    <div className="relative mb-6 flex justify-center">
      <div className="w-full max-w-2xl relative">
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
          <FaSearch />
        </div>
        <input
          type="text"
          value={value}
          onChange={onChange}
          className="w-full pl-12 pr-4 py-3 bg-transparent border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition-shadow text-sm"
          aria-label="Search news"
        />
      </div>
    </div>
  );
}