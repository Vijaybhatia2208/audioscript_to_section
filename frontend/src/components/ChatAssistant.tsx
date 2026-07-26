import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { queryYouTubeVideo } from '../api/yt';
import type { SourceCitation } from '../api/yt';

import { Send, Bot, User, Clock, Sparkles, Loader2 } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  sources?: SourceCitation[];
}

interface ChatAssistantProps {
  videoId: string;
  onSeek: (seconds: number) => void;
}

export const ChatAssistant: React.FC<ChatAssistantProps> = ({ videoId, onSeek }) => {
  const [inputQuery, setInputQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Hello! I am your YouTube AI Co-Pilot. Ask me anything about this video, and I will answer with exact 1-click video timestamp links!',
    },
  ]);

  const chatMutation = useMutation({
    mutationFn: (queryText: string) => queryYouTubeVideo(videoId, queryText),
    onSuccess: (data) => {
      const aiMessage: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        text: data.answer,
        sources: data.sources,
      };
      setMessages((prev) => [...prev, aiMessage]);
    },
    onError: (error: any) => {
      const errorMessage: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        text: `Error: ${error?.response?.data?.detail || error.message || 'Failed to process question.'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || chatMutation.isPending) return;

    const userText = inputQuery.trim();
    setInputQuery('');

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
    };

    setMessages((prev) => [...prev, userMessage]);
    chatMutation.mutate(userText);
  };

  const samplePrompts = [
    'What is the main topic of this video?',
    'What key concepts are explained?',
    'Where is the main code example shown?',
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl h-[580px] flex flex-col backdrop-blur-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 bg-purple-500/20 text-purple-400 rounded-lg border border-purple-500/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Learning Assistant</h3>
            <p className="text-[11px] text-slate-400">Ask questions & jump to exact timestamps</p>
          </div>
        </div>
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${
              msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div
              className={`p-2 rounded-xl shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-purple-400 border border-slate-700'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/20'
                  : 'bg-slate-950/80 border border-slate-800 text-slate-200 shadow-md'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>

              {/* Source Timestamp Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-800/80">
                  <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1.5 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-purple-400" /> Click to Jump in Video:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.sources.map((src, i) => {
                      const sec = src.start_sec || 0;
                      return (
                        <button
                          key={i}
                          onClick={() => onSeek(sec)}
                          className="px-2 py-1 bg-purple-500/10 hover:bg-purple-500/25 border border-purple-500/30 text-purple-300 hover:text-white text-[10px] font-mono font-semibold rounded-md transition-all flex items-center gap-1 cursor-pointer"
                        >
                          <Clock className="w-2.5 h-2.5 text-purple-400" />
                          {src.timestamp_range || `${Math.floor(sec / 60)}:${Math.floor(sec % 60)}`}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {chatMutation.isPending && (
          <div className="flex items-center space-x-3 text-slate-400 text-xs p-2">
            <div className="p-2 bg-slate-800 rounded-xl">
              <Bot className="w-4 h-4 text-purple-400 animate-pulse" />
            </div>
            <div className="flex items-center space-x-2 bg-slate-950/80 border border-slate-800 px-3 py-2 rounded-xl">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" />
              <span>Analyzing transcript & generating answer...</span>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompts */}
      {messages.length === 1 && (
        <div className="px-4 py-2 flex flex-wrap gap-1.5 border-t border-slate-800/50 bg-slate-950/40">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setInputQuery(p);
              }}
              className="text-[11px] text-slate-400 hover:text-purple-300 bg-slate-900 border border-slate-800 hover:border-purple-500/30 px-2.5 py-1 rounded-lg transition-all cursor-pointer"
            >
              💡 {p}
            </button>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <form onSubmit={handleSend} className="p-3 bg-slate-950/90 border-t border-slate-800/80 flex items-center space-x-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask a question about this video..."
          className="flex-1 bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 px-3.5 py-2.5 rounded-xl focus:outline-none focus:border-purple-500/60"
        />
        <button
          type="submit"
          disabled={!inputQuery.trim() || chatMutation.isPending}
          className="p-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-xl shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
