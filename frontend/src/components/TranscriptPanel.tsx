import React, { useState } from 'react';
import type { Cue } from '../api/yt';

import { Search, Clock, FileText } from 'lucide-react';

interface TranscriptPanelProps {
  cues: Cue[];
  onSeek: (seconds: number) => void;
}

export const TranscriptPanel: React.FC<TranscriptPanelProps> = ({ cues, onSeek }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCues = cues.filter((c) =>
    c.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 h-[450px] flex flex-col backdrop-blur-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
        <div className="flex items-center space-x-2 text-slate-200">
          <FileText className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-semibold">Video Transcript ({cues.length} cues)</h3>
        </div>

        {/* Search inside transcript */}
        <div className="relative w-48">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search transcript..."
            className="w-full bg-slate-950/80 border border-slate-800 text-xs text-slate-200 pl-8 pr-2 py-1.5 rounded-lg focus:outline-none focus:border-purple-500/50"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {filteredCues.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-slate-500">
            No matching transcript lines found.
          </div>
        ) : (
          filteredCues.map((cue) => (
            <div
              key={cue.index}
              onClick={() => onSeek(cue.start_sec)}
              className="group p-2.5 bg-slate-950/40 hover:bg-purple-900/10 border border-slate-800/50 hover:border-purple-500/30 rounded-xl transition-all cursor-pointer flex items-start space-x-3"
            >
              <span className="px-2 py-1 bg-purple-500/10 group-hover:bg-purple-500/20 text-purple-300 text-[11px] font-mono font-medium rounded-md border border-purple-500/20 flex items-center gap-1 shrink-0">
                <Clock className="w-3 h-3 text-purple-400" />
                {cue.start_time_str}
              </span>
              <p className="text-xs text-slate-300 group-hover:text-white transition-colors leading-relaxed">
                {cue.text}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
