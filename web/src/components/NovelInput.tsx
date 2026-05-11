import { useAppStore } from '@/store';
import { FileText, Upload } from 'lucide-react';

export function NovelInput() {
  const { params, setParams } = useAppStore();

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setParams({ novelText: e.target.value });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        setParams({ novelText: text });
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-[var(--accent-primary)]" />
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">小说输入</h2>
      </div>
      
      <textarea
        value={params.novelText || ''}
        onChange={handleTextChange}
        placeholder="在此粘贴小说文本，或上传文本文件..."
        className="input-base min-h-[256px] resize-none"
      />
      
      <div className="mt-4 flex items-center gap-4">
        <label className="btn-ghost flex items-center gap-2 cursor-pointer">
          <Upload className="w-4 h-4" />
          <span>上传文件</span>
          <input
            type="file"
            accept=".txt,.md"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
        
        <span className="text-sm text-[var(--text-tertiary)]">
          字数: {(params.novelText || '').length}
        </span>
      </div>
    </div>
  );
}
