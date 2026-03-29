import React, { useRef, useImperativeHandle, forwardRef } from 'react';

interface Props {
  src: string;
  onTimeUpdate?: (time: number) => void;
}

export interface VideoPlayerRef {
  seek: (time: number) => void;
  getCurrentTime: () => number;
}

const VideoPlayer = forwardRef<VideoPlayerRef, Props>(({ src, onTimeUpdate }, ref) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useImperativeHandle(ref, () => ({
    seek: (time: number) => {
      if (videoRef.current) videoRef.current.currentTime = time;
    },
    getCurrentTime: () => videoRef.current?.currentTime || 0,
  }));

  return (
    <div style={{ width: '100%', background: '#000', borderRadius: '8px', overflow: 'hidden' }}>
      <video
        ref={videoRef}
        src={src}
        controls
        style={{ width: '100%', maxHeight: '500px' }}
        onTimeUpdate={() => onTimeUpdate?.(videoRef.current?.currentTime || 0)}
      />
    </div>
  );
});

VideoPlayer.displayName = 'VideoPlayer';
export default VideoPlayer;
