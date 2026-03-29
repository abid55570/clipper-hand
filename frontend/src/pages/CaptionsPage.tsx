import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import CaptionEditor from '../components/captions/CaptionEditor';
import CaptionStyler from '../components/captions/CaptionStyler';
import CaptionPreview from '../components/captions/CaptionPreview';
import { getVideoCaptions, updateCaptionStyle, transcribeVideo } from '../api/captions';
import type { Caption, CaptionStyle } from '../types';

export default function CaptionsPage() {
  const { videoId } = useParams<{ videoId: string }>();
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [style, setStyle] = useState<CaptionStyle>({
    font_family: 'Arial', font_size: 48, primary_color: '#FFFFFF',
    outline_color: '#000000', highlight_color: '#FFFF00',
    highlight_words: [], position: 'bottom', bold: false, animation_type: 'none',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (videoId) loadCaptions();
  }, [videoId]);

  const loadCaptions = async () => {
    if (!videoId) return;
    const data = await getVideoCaptions(videoId);
    setCaptions(data.captions || []);
  };

  const handleTranscribe = async () => {
    if (!videoId) return;
    setLoading(true);
    await transcribeVideo(videoId);
    setLoading(false);
    // Poll for results
    const interval = setInterval(async () => {
      await loadCaptions();
    }, 3000);
    setTimeout(() => clearInterval(interval), 120000);
  };

  const handleStyleChange = async (newStyle: CaptionStyle) => {
    setStyle(newStyle);
    if (captions.length > 0) {
      await updateCaptionStyle(captions[0].id, newStyle);
    }
  };

  const previewText = captions[0]?.segments[0]?.text || 'Sample caption text for preview';

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>Captions</h1>

      {captions.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ marginBottom: '12px' }}>No captions yet. Transcribe the video first.</p>
          <button className="btn btn-primary" onClick={handleTranscribe} disabled={loading}>
            {loading ? 'Starting...' : 'Transcribe Video'}
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <CaptionEditor caption={captions[0]} />
          </div>
          <div>
            <CaptionPreview text={previewText} style={style} />
            <div style={{ marginTop: '16px' }}>
              <CaptionStyler onStyleChange={handleStyleChange} initialStyle={style} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
