import { Image, Download, Play, Film } from 'lucide-react';
import { comfyUIClient } from '@/lib/comfyui-client';

interface ResultGalleryProps {
  outputs: any[];
}

export function ResultGallery({ outputs }: ResultGalleryProps) {
  if (outputs.length === 0) return null;

  const renderOutput = (output: any, idx: number) => {
    if (output.images && Array.isArray(output.images)) {
      return output.images.map((img: any, imgIdx: number) => {
        const imageUrl = comfyUIClient.getImageUrl(img.filename, img.subfolder, img.type);
        return (
          <div key={`${idx}-${imgIdx}`} className="card overflow-hidden">
            <img src={imageUrl} alt={`Output ${idx}-${imgIdx}`} className="w-full h-48 object-cover" />
            <div className="p-3">
              <p className="text-sm text-[var(--text-secondary)] truncate">{img.filename}</p>
              <a href={imageUrl} download={img.filename} className="mt-2 flex items-center gap-1 text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)]">
                <Download className="w-4 h-4" /><span>下载</span>
              </a>
            </div>
          </div>
        );
      });
    }

    if (output.videos && Array.isArray(output.videos)) {
      return output.videos.map((video: any, videoIdx: number) => {
        const videoUrl = comfyUIClient.getImageUrl(video.filename, video.subfolder, video.type);
        return (
          <div key={`${idx}-${videoIdx}`} className="card overflow-hidden">
            <video src={videoUrl} controls className="w-full h-48 object-cover" />
            <div className="p-3">
              <p className="text-sm text-[var(--text-secondary)] truncate">{video.filename}</p>
              <a href={videoUrl} download={video.filename} className="mt-2 flex items-center gap-1 text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)]">
                <Download className="w-4 h-4" /><span>下载</span>
              </a>
            </div>
          </div>
        );
      });
    }

    if (output.audio && Array.isArray(output.audio)) {
      return output.audio.map((audio: any, audioIdx: number) => {
        const audioUrl = comfyUIClient.getImageUrl(audio.filename, audio.subfolder, audio.type);
        return (
          <div key={`${idx}-${audioIdx}`} className="card p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[var(--bg-tertiary)] rounded-full flex items-center justify-center">
                <Play className="w-6 h-6 text-[var(--accent-primary)]" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-[var(--text-primary)] truncate">{audio.filename}</p>
                <audio src={audioUrl} controls className="w-full mt-2" />
              </div>
            </div>
            <a href={audioUrl} download={audio.filename} className="mt-2 flex items-center gap-1 text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)]">
              <Download className="w-4 h-4" /><span>下载</span>
            </a>
          </div>
        );
      });
    }

    if (output.text) {
      const text = typeof output.text === 'string' ? output.text : JSON.stringify(output.text, null, 2);
      const isStoryboard = text.includes('"storyboard"') || text.includes('"segments"');
      return (
        <div className="card p-4">
          <div className="flex items-center gap-2 mb-2">
            {isStoryboard && <Film className="w-4 h-4 text-[var(--accent-primary)]" />}
            <p className="text-sm font-medium text-[var(--text-primary)]">{isStoryboard ? '故事板结果' : '文本输出'}</p>
          </div>
          <pre className="text-xs text-[var(--text-secondary)] bg-[var(--bg-primary)] p-3 rounded overflow-auto max-h-64">{text}</pre>
        </div>
      );
    }

    return null;
  };

  const hasContent = outputs.some((o) =>
    (o.images && o.images.length > 0) ||
    (o.videos && o.videos.length > 0) ||
    (o.audio && o.audio.length > 0) ||
    o.text
  );

  if (!hasContent) return null;

  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <Image className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">生成结果</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {outputs.map((output, idx) => renderOutput(output, idx))}
      </div>
    </div>
  );
}
