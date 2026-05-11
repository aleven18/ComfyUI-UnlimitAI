import { useState } from 'react';
import { 
  Image, 
  Video, 
  Music, 
  FileText, 
  Trash2, 
  Download,
  Grid,
  List,
  Search
} from 'lucide-react';

type ResourceTab = 'images' | 'videos' | 'audio' | 'documents';
type ViewMode = 'grid' | 'list';

interface Resource {
  id: string;
  name: string;
  type: 'image' | 'video' | 'audio' | 'document';
  size: string;
  createdAt: string;
  url: string;
  thumbnail?: string;
}

const mockResources: Record<ResourceTab, Resource[]> = {
  images: [
    { id: '1', name: 'scene_001.png', type: 'image', size: '2.3 MB', createdAt: '2024-01-15 10:30', url: '', thumbnail: '' },
    { id: '2', name: 'scene_002.png', type: 'image', size: '1.8 MB', createdAt: '2024-01-15 10:35', url: '', thumbnail: '' },
    { id: '3', name: 'character_001.png', type: 'image', size: '3.1 MB', createdAt: '2024-01-15 11:20', url: '', thumbnail: '' },
  ],
  videos: [
    { id: '4', name: 'final_video.mp4', type: 'video', size: '45.2 MB', createdAt: '2024-01-15 14:20', url: '', thumbnail: '' },
  ],
  audio: [
    { id: '5', name: 'background_music.mp3', type: 'audio', size: '5.6 MB', createdAt: '2024-01-15 12:15', url: '', thumbnail: '' },
    { id: '6', name: 'dialogue_001.wav', type: 'audio', size: '2.1 MB', createdAt: '2024-01-15 12:20', url: '', thumbnail: '' },
  ],
  documents: [
    { id: '7', name: 'script.txt', type: 'document', size: '12 KB', createdAt: '2024-01-15 09:00', url: '', thumbnail: '' },
    { id: '8', name: 'storyboard.json', type: 'document', size: '8 KB', createdAt: '2024-01-15 10:00', url: '', thumbnail: '' },
  ]
};

export function ResourceManager() {
  const [activeTab, setActiveTab] = useState<ResourceTab>('images');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  
  const resources = mockResources[activeTab];
  
  const filteredResources = resources.filter(r =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const tabs: { id: ResourceTab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'images', label: '图片', icon: <Image className="w-4 h-4" />, count: mockResources.images.length },
    { id: 'videos', label: '视频', icon: <Video className="w-4 h-4" />, count: mockResources.videos.length },
    { id: 'audio', label: '音频', icon: <Music className="w-4 h-4" />, count: mockResources.audio.length },
    { id: 'documents', label: '文档', icon: <FileText className="w-4 h-4" />, count: mockResources.documents.length },
  ];
  
  const toggleSelect = (id: string) => {
    setSelectedItems(prev =>
      prev.includes(id)
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };
  
  const handleDelete = (id: string) => {
    if (confirm('确定要删除这个资源吗？')) {
      console.log('Delete resource:', id);
    }
  };
  
  const handleDownload = (resource: Resource) => {
    console.log('Download resource:', resource.name);
  };
  
  return (
    <div className="h-full flex flex-col bg-[var(--bg-primary)]">
      {/* Tab Header */}
      <div className="border-b border-[var(--border-subtle)] px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  h-9 px-4 flex items-center gap-2 text-[13px] font-medium rounded-lg transition-all
                  ${activeTab === tab.id 
                    ? 'bg-[var(--accent-primary)] text-white' 
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                  }
                `}
              >
                {tab.icon}
                {tab.label}
                <span className={`px-1.5 py-0.5 text-[10px] rounded-full ${
                  activeTab === tab.id 
                    ? 'bg-[var(--bg-tertiary)]' 
                    : 'bg-[var(--bg-tertiary)]'
                }`}>
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'grid' 
                  ? 'bg-[var(--accent-primary)] text-white' 
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${
                viewMode === 'list' 
                  ? 'bg-[var(--accent-primary)] text-white' 
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Toolbar */}
      <div className="border-b border-[var(--border-subtle)] px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索资源..."
              className="w-full pl-9 pr-4 py-2 bg-[var(--bg-primary)] border border-[var(--border-default)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]"
            />
          </div>
          
          {selectedItems.length > 0 && (
            <button className="btn-secondary flex items-center gap-2 text-[var(--accent-error)]">
              <Trash2 className="w-4 h-4" />
              删除 ({selectedItems.length})
            </button>
          )}
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {filteredResources.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              {activeTab === 'images' && <Image className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />}
              {activeTab === 'videos' && <Video className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />}
              {activeTab === 'audio' && <Music className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />}
              {activeTab === 'documents' && <FileText className="w-16 h-16 mx-auto mb-4 text-[var(--text-tertiary)] opacity-50" />}
              <p className="text-sm text-[var(--text-tertiary)]">
                {searchQuery ? '没有找到匹配的资源' : '还没有资源'}
              </p>
            </div>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filteredResources.map((resource) => (
              <div
                key={resource.id}
                className={`
                  group relative bg-[var(--bg-primary)] border rounded-lg overflow-hidden cursor-pointer transition-all
                  ${selectedItems.includes(resource.id) 
                    ? 'border-[var(--accent-primary)] ring-2 ring-[var(--accent-primary)]' 
                    : 'border-[var(--border-default)] hover:border-[var(--accent-primary)]'
                  }
                `}
                onClick={() => toggleSelect(resource.id)}
              >
                <div className="aspect-square bg-[var(--bg-secondary)] flex items-center justify-center">
                  {activeTab === 'images' && <Image className="w-12 h-12 text-[var(--text-tertiary)]" />}
                  {activeTab === 'videos' && <Video className="w-12 h-12 text-[var(--text-tertiary)]" />}
                  {activeTab === 'audio' && <Music className="w-12 h-12 text-[var(--text-tertiary)]" />}
                  {activeTab === 'documents' && <FileText className="w-12 h-12 text-[var(--text-tertiary)]" />}
                </div>
                
                <div className="p-3">
                  <p className="text-sm font-medium truncate">{resource.name}</p>
                  <p className="text-xs text-[var(--text-tertiary)] mt-1">{resource.size}</p>
                </div>
                
                <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDownload(resource); }}
                    className="p-1.5 bg-[var(--bg-primary)] rounded shadow-sm hover:bg-[var(--bg-hover)]"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(resource.id); }}
                    className="p-1.5 bg-[var(--bg-primary)] rounded shadow-sm hover:bg-red-50 dark:hover:bg-red-900/20 text-[var(--accent-error)]"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {filteredResources.map((resource) => (
              <div
                key={resource.id}
                className={`
                  flex items-center gap-4 p-3 bg-[var(--bg-primary)] border rounded-lg cursor-pointer transition-all
                  ${selectedItems.includes(resource.id) 
                    ? 'border-[var(--accent-primary)] ring-2 ring-[var(--accent-primary)]' 
                    : 'border-[var(--border-default)] hover:border-[var(--accent-primary)]'
                  }
                `}
                onClick={() => toggleSelect(resource.id)}
              >
                <div className="w-12 h-12 bg-[var(--bg-secondary)] rounded flex items-center justify-center flex-shrink-0">
                  {activeTab === 'images' && <Image className="w-6 h-6 text-[var(--text-tertiary)]" />}
                  {activeTab === 'videos' && <Video className="w-6 h-6 text-[var(--text-tertiary)]" />}
                  {activeTab === 'audio' && <Music className="w-6 h-6 text-[var(--text-tertiary)]" />}
                  {activeTab === 'documents' && <FileText className="w-6 h-6 text-[var(--text-tertiary)]" />}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{resource.name}</p>
                  <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{resource.createdAt}</p>
                </div>
                
                <div className="text-sm text-[var(--text-tertiary)] flex-shrink-0">
                  {resource.size}
                </div>
                
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDownload(resource); }}
                    className="p-2 hover:bg-[var(--bg-hover)] rounded-lg"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(resource.id); }}
                    className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 text-[var(--accent-error)] rounded-lg"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
