/**
 * 角色参考图选择组件
 * 
 * 功能：
 * 1. 显示生成的多张参考图
 * 2. 用户选择至少3张图片
 * 3. 智能推荐最佳选择
 * 4. 强制选择限制
 */

import { useState } from 'react';

interface GeneratedImage {
  index: number;
  url: string;
  prompt: string;
  composition: string;
  variation: string;
  seed: number;
  quality_score: number;
}

interface CharacterImageSelectorProps {
  characterName: string;
  generatedImages: GeneratedImage[];
  minSelections: number;
  maxSelections: number;
  onConfirm: (selectedImages: GeneratedImage[]) => void;
  onRegenerate: () => void;
}

export function CharacterImageSelector({
  characterName,
  generatedImages,
  minSelections,
  maxSelections,
  onConfirm,
  onRegenerate
}: CharacterImageSelectorProps) {
  const [selectedImages, setSelectedImages] = useState<Set<number>>(new Set());
  const [previewImage, setPreviewImage] = useState<GeneratedImage | null>(null);

  const toggleImage = (image: GeneratedImage) => {
    const newSelection = new Set(selectedImages);
    
    if (newSelection.has(image.index)) {
      newSelection.delete(image.index);
    } else {
      if (newSelection.size >= maxSelections) {
        alert(`最多只能选择 ${maxSelections} 张图片`);
        return;
      }
      newSelection.add(image.index);
    }
    
    setSelectedImages(newSelection);
  };

  const handleConfirm = () => {
    if (selectedImages.size < minSelections) {
      alert(`请至少选择 ${minSelections} 张图片`);
      return;
    }

    const selected = generatedImages.filter(img => selectedImages.has(img.index));
    onConfirm(selected);
  };

  const getQualityStars = (score: number) => {
    const fullStars = Math.floor(score * 5);
    const halfStar = (score * 5) % 1 >= 0.5;
    
    return '⭐'.repeat(fullStars) + (halfStar ? '⭐' : '');
  };

  return (
    <div className="space-y-6">
      {/* 标题和信息 */}
      <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-2">
          角色参考图选择 - {characterName}
        </h3>
        <p className="text-sm text-[var(--text-tertiary)]">
          系统已生成 {generatedImages.length} 张参考图，请至少选择 {minSelections} 张
        </p>
      </div>

      {/* 智能推荐 */}
      <div className="bg-[var(--accent-primary)]/10 border border-[var(--accent-primary)]/30 rounded-lg p-4">
        <h4 className="font-semibold text-sm mb-2">💡 智能推荐</h4>
        <p className="text-xs text-[var(--text-tertiary)] mb-2">
          根据质量评分和构图多样性，系统推荐以下选择：
        </p>
        <div className="flex gap-2">
          {generatedImages.slice(0, 3).map(img => (
            <span
              key={img.index}
              className="px-3 py-1 bg-[var(--accent-primary)] text-white text-xs rounded-full"
            >
              图片{img.index} ({img.composition})
            </span>
          ))}
        </div>
      </div>

      {/* 图片网格 */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {generatedImages.map(image => (
          <div
            key={image.index}
            className={`
              relative rounded-lg overflow-hidden cursor-pointer transition-all
              ${selectedImages.has(image.index)
                ? 'ring-4 ring-[var(--accent-primary)]'
                : 'ring-2 ring-transparent hover:ring-[var(--border-default)]'
              }
            `}
            onClick={() => toggleImage(image)}
          >
            {/* 图片 */}
            <div className="aspect-[3/4] bg-[var(--bg-tertiary)] relative">
              <img
                src={image.url}
                alt={`参考图 ${image.index}`}
                className="w-full h-full object-cover"
              />
              
              {/* 选中标记 */}
              {selectedImages.has(image.index) && (
                <div className="absolute top-2 right-2 w-8 h-8 bg-[var(--success)] rounded-full flex items-center justify-center text-white font-bold">
                  ✓
                </div>
              )}

              {/* 悬停预览按钮 */}
              <button
                className="absolute bottom-2 right-2 w-10 h-10 bg-black/60 rounded-full flex items-center justify-center text-white hover:bg-black/80 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setPreviewImage(image);
                }}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
              </button>
            </div>

            {/* 图片信息 */}
            <div className="p-3 bg-[var(--bg-secondary)]">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium">
                  图片 {image.index}
                </span>
                <span className="text-xs text-[var(--text-tertiary)]">
                  {getQualityStars(image.quality_score)}
                </span>
              </div>
              <div className="text-xs text-[var(--text-tertiary)] space-y-0.5">
                <div>构图: {image.composition}</div>
                <div>变体: {image.variation}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 选择统计 */}
      <div className="bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium">已选择 {selectedImages.size} 张</span>
          <span className="text-xs text-[var(--text-tertiary)]">
            {selectedImages.size < minSelections 
              ? `还需选择 ${minSelections - selectedImages.size} 张` 
              : '已满足最低要求'}
          </span>
        </div>

        {/* 选择的图片预览 */}
        {selectedImages.size > 0 && (
          <div className="flex gap-2 mb-3">
            {Array.from(selectedImages).map(index => {
              const img = generatedImages.find(i => i.index === index);
              return img ? (
                <div key={index} className="relative group">
                  <img
                    src={img.url}
                    alt={`已选 ${index}`}
                    className="w-16 h-20 object-cover rounded"
                  />
                  <button
                    className="absolute -top-1 -right-1 w-5 h-5 bg-[var(--error)] rounded-full text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => toggleImage(img)}
                  >
                    ×
                  </button>
                </div>
              ) : null;
            })}
          </div>
        )}

        {/* 进度条 */}
        <div className="relative h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-[var(--success)] transition-all"
            style={{ width: `${Math.min(100, (selectedImages.size / minSelections) * 100)}%` }}
          />
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-3">
        <button
          onClick={handleConfirm}
          disabled={selectedImages.size < minSelections}
          className="flex-1 py-3 bg-[var(--success)] text-white rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ✅ 确认选择 ({selectedImages.size}/{minSelections}~{maxSelections})
        </button>
        
        <button
          onClick={onRegenerate}
          className="px-6 py-3 bg-[var(--bg-tertiary)] border border-[var(--border-default)] rounded-lg font-medium hover:bg-[var(--bg-primary)]"
        >
          🔄 重新生成
        </button>
      </div>

      {/* 图片预览弹窗 */}
      {previewImage && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-6"
          onClick={() => setPreviewImage(null)}
        >
          <div className="relative max-w-4xl w-full" onClick={e => e.stopPropagation()}>
            <button
              className="absolute -top-12 right-0 text-white text-4xl hover:opacity-80"
              onClick={() => setPreviewImage(null)}
            >
              ×
            </button>
            
            <img
              src={previewImage.url}
              alt={`预览图片 ${previewImage.index}`}
              className="w-full rounded-lg"
            />
            
            <div className="mt-4 bg-white/10 backdrop-blur rounded-lg p-4 text-white">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-white/60">构图:</span>
                  <span className="ml-2">{previewImage.composition}</span>
                </div>
                <div>
                  <span className="text-white/60">变体:</span>
                  <span className="ml-2">{previewImage.variation}</span>
                </div>
                <div>
                  <span className="text-white/60">质量评分:</span>
                  <span className="ml-2">{getQualityStars(previewImage.quality_score)}</span>
                </div>
                <div>
                  <span className="text-white/60">Seed:</span>
                  <span className="ml-2 font-mono">{previewImage.seed}</span>
                </div>
              </div>
              <div className="mt-2 text-xs text-white/60">
                提示词: {previewImage.prompt}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
