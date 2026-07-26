import React, { useState, useRef } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { ClerkProvider } from '@clerk/clerk-react';
import { Navbar } from './components/Navbar';
import { UrlInput } from './components/UrlInput';
import { VideoPlayer } from './components/VideoPlayer';
import { TranscriptPanel } from './components/TranscriptPanel';
import { ChatAssistant } from './components/ChatAssistant';
import { fetchYouTubeTranscript } from './api/yt';
import { Video, ListFilter, AlertCircle } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!CLERK_PUBLISHABLE_KEY) {
  console.warn('Missing VITE_CLERK_PUBLISHABLE_KEY in frontend/.env file.');
}

const MainApp: React.FC = () => {
  const [activeUrl, setActiveUrl] = useState('https://www.youtube.com/watch?v=bMknfKXIFA8');
  const [activeTab, setActiveTab] = useState<'transcript' | 'chat'>('chat');
  const playerRef = useRef<any>(null);

  // TanStack React Query for fetching video transcript & metadata
  const {
    data: videoInfo,
    isLoading,
    isError,
    error,
  } = useQuery({

    queryKey: ['videoInfo', activeUrl],
    queryFn: () => fetchYouTubeTranscript(activeUrl),
    enabled: !!activeUrl,
  });

  const handleAnalyze = (url: string) => {
    setActiveUrl(url);
  };

  const handleSeek = (seconds: number) => {
    if (playerRef.current) {
      playerRef.current.seekTo(seconds, true);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-4 flex flex-col">
        {/* Top URL Input Bar */}
        <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} activeUrl={activeUrl} />

        {isError && (
          <div className="max-w-4xl mx-auto mb-6 w-full p-4 bg-red-950/50 border border-red-800/80 rounded-2xl flex items-center space-x-3 text-red-300 text-xs">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-400" />
            <p>
              Failed to load video transcript: {(error as any)?.response?.data?.detail || (error as Error).message}. Make sure the YouTube video has public subtitles enabled.
            </p>
          </div>
        )}

        {videoInfo && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start flex-1">
            {/* Left Column: Video Player & Transcript */}
            <div className="lg:col-span-7 flex flex-col space-y-4">
              {/* Embedded YouTube Player */}
              <VideoPlayer videoId={videoInfo.video_id} onReady={(player) => (playerRef.current = player)} />

              {/* Video Title & Meta */}
              <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between backdrop-blur-xl">
                <div>
                  <h2 className="text-sm font-semibold text-white truncate max-w-md">
                    YouTube Video: <span className="text-purple-400">{videoInfo.video_id}</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Duration: {videoInfo.total_duration_str} • {videoInfo.cue_count} Transcript Lines
                  </p>
                </div>

                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
                  <button
                    onClick={() => setActiveTab('chat')}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 cursor-pointer ${
                      activeTab === 'chat'
                        ? 'bg-purple-600 text-white shadow-md'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <Video className="w-3.5 h-3.5" /> AI Chat
                  </button>
                  <button
                    onClick={() => setActiveTab('transcript')}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 cursor-pointer ${
                      activeTab === 'transcript'
                        ? 'bg-purple-600 text-white shadow-md'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    <ListFilter className="w-3.5 h-3.5" /> Transcript
                  </button>
                </div>
              </div>

              {/* Full Transcript Panel */}
              {activeTab === 'transcript' && (
                <TranscriptPanel cues={videoInfo.cues} onSeek={handleSeek} />
              )}
            </div>

            {/* Right Column: AI Chat Assistant */}
            <div className="lg:col-span-5">
              <ChatAssistant videoId={videoInfo.video_id} onSeek={handleSeek} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default function App() {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <QueryClientProvider client={queryClient}>
        <MainApp />
      </QueryClientProvider>
    </ClerkProvider>
  );
}
