import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useVideoStore, useClipStore, useJobStore } from '../store';
import VideoPlayer, { VideoPlayerRef } from '../components/video/VideoPlayer';
import Timeline from '../components/video/Timeline';
import TimestampInput from '../components/video/TimestampInput';
import ClipList from '../components/clips/ClipList';
import HighlightSuggestions from '../components/ai/HighlightSuggestions';
import JobStatus from '../components/common/JobStatus';
import { useJobPolling } from '../hooks/useJobPolling';
import { detectHighlights, getHighlights } from '../api/ai';
import { transcribeVideo } from '../api/captions';
import { deleteClip } from '../api/clips';
import type { Highlight, ClipTimestamp } from '../types';

export default function EditorPage() {
  const { videoId } = useParams<{ videoId: string }>();
  const navigate = useNavigate();
  const { currentVideo, fetchVideo } = useVideoStore();
  const { clips, timestamps, fetchClips, addTimestamp, removeTimestamp, clearTimestamps, submitClips } = useClipStore();
  const playerRef = useRef<VideoPlayerRef>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const { job: activeJob } = useJobPolling(activeJobId);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [activeTab, setActiveTab] = useState<'clips' | 'ai' | 'captions'>('clips');

  useEffect(() => {
    if (videoId) {
      fetchVideo(videoId);
      fetchClips(videoId);
    }
  }, [videoId, fetchVideo, fetchClips]);

  // Refresh clips when job completes
  useEffect(() => {
    if (activeJob?.status === 'completed' && videoId) {
      fetchClips(videoId);
    }
  }, [activeJob?.status, videoId, fetchClips]);

  const handleGenerateClips = async () => {
    if (!videoId || timestamps.length === 0) return;
    try {
      const result = await submitClips(videoId);
      setActiveJobId(result.job_id);
    } catch {
      // error handled by store
    }
  };

  const handleDetectHighlights = async () => {
    if (!videoId) return;
    const { job_id } = await detectHighlights(videoId);
    setActiveJobId(job_id);
    // Poll and then fetch highlights
    const interval = setInterval(async () => {
      try {
        const { highlights: h } = await getHighlights(videoId);
        if (h.length > 0) {
          setHighlights(h);
          clearInterval(interval);
        }
      } catch { /* keep polling */ }
    }, 3000);
    setTimeout(() => clearInterval(interval), 60000);
  };

  const handleTranscribe = async () => {
    if (!videoId) return;
    const { job_id } = await transcribeVideo(videoId);
    setActiveJobId(job_id);
  };

  const handleAcceptHighlight = (ts: ClipTimestamp) => addTimestamp(ts);
  const handleAcceptAll = () => highlights.forEach(h =>
    addTimestamp({ start: h.start_time, end: h.end_time, label: `Highlight (${h.source})` })
  );

  const handleDeleteClip = async (clipId: string) => {
    await deleteClip(clipId);
    if (videoId) fetchClips(videoId);
  };

  if (!currentVideo) {
    return <p style={{ color: 'var(--text-secondary)' }}>Loading video...</p>;
  }

  const videoSrc = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/clips/${videoId}/download`;

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '16px' }}>{currentVideo.original_name}</h1>

      {/* Player */}
      <VideoPlayer ref={playerRef} src={videoSrc} onTimeUpdate={setCurrentTime} />
      <Timeline
        duration={currentVideo.duration_secs || 0}
        clips={timestamps}
        currentTime={currentTime}
        onSeek={(t) => playerRef.current?.seek(t)}
      />

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginTop: '20px', marginBottom: '16px' }}>
        {(['clips', 'ai', 'captions'] as const).map((tab) => (
          <button key={tab} className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setActiveTab(tab)}>
            {tab === 'clips' ? 'Clips' : tab === 'ai' ? 'AI Tools' : 'Captions'}
          </button>
        ))}
      </div>

      {/* Active Job Status */}
      {activeJob && <JobStatus job={activeJob} />}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '12px' }}>
        {/* Left panel */}
        <div>
          {activeTab === 'clips' && (
            <>
              <div className="card">
                <h3 style={{ marginBottom: '12px' }}>Add Clip Timestamps</h3>
                <TimestampInput onAdd={addTimestamp} videoDuration={currentVideo.duration_secs || undefined} />
                {timestamps.length > 0 && (
                  <>
                    <div style={{ marginTop: '12px' }}>
                      {timestamps.map((ts, i) => (
                        <div key={i} style={{
                          display: 'flex', justifyContent: 'space-between', padding: '6px 0',
                          borderBottom: '1px solid var(--border)',
                        }}>
                          <span>{ts.label}: {ts.start}s - {ts.end}s</span>
                          <button className="btn btn-danger" style={{ fontSize: '11px', padding: '2px 8px' }}
                                  onClick={() => removeTimestamp(i)}>Remove</button>
                        </div>
                      ))}
                    </div>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                      <button className="btn btn-primary" onClick={handleGenerateClips}>
                        Generate {timestamps.length} Clips
                      </button>
                      <button className="btn btn-outline" onClick={clearTimestamps}>Clear All</button>
                    </div>
                  </>
                )}
              </div>
            </>
          )}

          {activeTab === 'ai' && (
            <div className="card">
              <h3 style={{ marginBottom: '12px' }}>AI Tools</h3>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <button className="btn btn-primary" onClick={handleDetectHighlights}>Detect Highlights</button>
                <button className="btn btn-outline" onClick={handleTranscribe}>Transcribe</button>
              </div>
              <HighlightSuggestions
                highlights={highlights}
                onAccept={handleAcceptHighlight}
                onAcceptAll={handleAcceptAll}
              />
            </div>
          )}

          {activeTab === 'captions' && (
            <div className="card">
              <h3 style={{ marginBottom: '12px' }}>Captions</h3>
              <button className="btn btn-primary" onClick={handleTranscribe}>Start Transcription</button>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '8px' }}>
                Transcribe the video to generate captions with word-level timestamps.
              </p>
            </div>
          )}
        </div>

        {/* Right panel: Clips */}
        <div>
          <h3 style={{ marginBottom: '12px' }}>Clips ({clips.length})</h3>
          <ClipList
            clips={clips}
            onDelete={handleDeleteClip}
            onExport={(clipId) => navigate(`/export/${clipId}`)}
          />
        </div>
      </div>
    </div>
  );
}
