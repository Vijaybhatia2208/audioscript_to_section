import React from 'react';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import { Video, Sparkles, LogIn } from 'lucide-react';


export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800 px-4 lg:px-8 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-purple-600 to-indigo-600 rounded-xl shadow-lg shadow-purple-500/20">
          <Video className="w-5 h-5 text-white" />
        </div>

        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold text-white tracking-tight">YouTube AI Co-Pilot</h1>
            <span className="px-2 py-0.5 text-[10px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-purple-400" /> RAG Powered
            </span>
          </div>
          <p className="text-xs text-slate-400">Instant AI Q&A with 1-Click Video Timestamp Seeking</p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="px-4 py-2 text-xs font-medium text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer">
              <LogIn className="w-3.5 h-3.5" /> Sign In
            </button>
          </SignInButton>
        </SignedOut>
        <SignedIn>
          <UserButton
            appearance={{
              elements: {
                userButtonAvatarBox: "w-9 h-9 border-2 border-purple-500/40"
              }
            }}
          />
        </SignedIn>
      </div>
    </header>
  );
};
