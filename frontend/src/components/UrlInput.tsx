import React, { useState } from 'react';
import { Video, Loader2, Sparkles } from 'lucide-react';

interface UrlInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
  activeUrl: string;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onAnalyze, isLoading, activeUrl }) => {
  const [inputUrl, setInputUrl] = useState(activeUrl || 'https://www.youtube.com/watch?v=bMknfKXIFA8');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputUrl.trim()) {
      onAnalyze(inputUrl.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto my-6 px-4">
      <div className="relative flex items-center bg-slate-900/90 border border-slate-800 focus-within:border-purple-500/60 focus-within:ring-2 focus-within:ring-purple-500/20 rounded-2xl p-2 shadow-2xl backdrop-blur-xl transition-all">
        <div className="pl-3 pr-2 text-slate-500">
          <Video className="w-5 h-5 text-red-500" />
        </div>

        <input
          type="text"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
          placeholder="Paste any YouTube video URL (e.g. https://www.youtube.com/watch?v=bMknfKXIFA8)..."
          className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none px-2"
        />
        <button
          type="submit"
          disabled={isLoading || !inputUrl.trim()}
          className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-purple-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shrink-0 cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Fetching Video...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" /> Analyze Video
            </>
          )}
        </button>
      </div>
    </form>
  );
};
