'use client';

import { useState } from 'react';

export default function WordCounter() {
  const [text, setText] = useState('');

  // 1. 글자수 계산 (공백 포함)
  const charCountWithSpaces = text.length;

  // 2. 글자수 계산 (공백 제외)
  const charCountWithoutSpaces = text.replace(/\s/g, '').length;

  // 3. 단어수 계산 (영어 에세이 핵심)
  const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;

  // 4. 예상 독서 시간 (분당 200단어 기준 계산)
  const readingTime = Math.ceil(wordCount / 200);

  // 액션 함수들
  const handleUpperCase = () => setText(text.toUpperCase());
  const handleLowerCase = () => setText(text.toLowerCase());
  const handleClear = () => setText('');
  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard! 🎉');
  };

  return (
    <main className="min-h-screen bg-slate-50 p-6 flex flex-col items-center justify-center">
      <div className="max-w-3xl w-full space-y-6">
        <h1 className="text-3xl font-bold text-slate-800 text-center">Smart Word Counter</h1>
        
        {/* 실시간 대시보드 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium">Words</p>
            <p className="text-2xl font-bold text-indigo-600">{wordCount}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium">Characters</p>
            <p className="text-2xl font-bold text-slate-800">{charCountWithSpaces}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium">Chars (No Space)</p>
            <p className="text-2xl font-bold text-slate-800">{charCountWithoutSpaces}</p>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 text-center">
            <p className="text-sm text-slate-500 font-medium">Reading Time</p>
            <p className="text-2xl font-bold text-emerald-600">~{readingTime} min</p>
          </div>
        </div>

        {/* 텍스트 입력창 */}
        <textarea
          className="w-full h-80 p-4 rounded-xl border border-slate-300 shadow-inner focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-slate-700 resize-none"
          placeholder="Paste your essay or text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        {/* 유틸리티 버튼 라인 */}
        <div className="flex flex-wrap gap-2 justify-end">
          <button onClick={handleUpperCase} className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition">AA UPPERCASE</button>
          <button onClick={handleLowerCase} className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition">aa lowercase</button>
          <button onClick={handleCopy} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition">📋 Copy</button>
          <button onClick={handleClear} className="px-4 py-2 bg-rose-50 text-rose-600 border border-rose-200 rounded-lg text-sm font-medium hover:bg-rose-100 transition">🗙 Clear</button>
        </div>
      </div>
    </main>
  );
}