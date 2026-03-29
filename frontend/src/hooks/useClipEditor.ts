import { useState, useCallback } from 'react';
import { trimClip, mergeClips } from '../api/clips';

export function useClipEditor() {
  const [trimming, setTrimming] = useState(false);
  const [merging, setMerging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTrim = useCallback(async (clipId: string, newStart: number, newEnd: number) => {
    setTrimming(true);
    setError(null);
    try {
      const result = await trimClip(clipId, newStart, newEnd);
      setTrimming(false);
      return result;
    } catch (err: any) {
      setError(err.message);
      setTrimming(false);
      throw err;
    }
  }, []);

  const handleMerge = useCallback(async (clipIds: string[], label?: string) => {
    setMerging(true);
    setError(null);
    try {
      const result = await mergeClips(clipIds, label);
      setMerging(false);
      return result;
    } catch (err: any) {
      setError(err.message);
      setMerging(false);
      throw err;
    }
  }, []);

  return { trimming, merging, error, handleTrim, handleMerge };
}
