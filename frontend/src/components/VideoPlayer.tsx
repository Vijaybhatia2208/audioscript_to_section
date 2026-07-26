import React from 'react';
import YouTube from 'react-youtube';
import type { YouTubeProps } from 'react-youtube';


interface VideoPlayerProps {
  videoId: string;
  onReady: (player: any) => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoId, onReady }) => {
  const opts: YouTubeProps['opts'] = {
    height: '100%',
    width: '100%',
    playerVars: {
      autoplay: 1,
      modestbranding: 1,
      rel: 0,
    },
  };

  const handleReady: YouTubeProps['onReady'] = (event) => {
    onReady(event.target);
  };

  return (
    <div className="relative w-full aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
      <YouTube
        videoId={videoId}
        opts={opts}
        onReady={handleReady}
        className="w-full h-full"
        iframeClassName="w-full h-full border-0 absolute top-0 left-0"
      />
    </div>
  );
};
