import { StoryboardTemplate } from '@/types';

export const STORYBOARD_TEMPLATES: StoryboardTemplate[] = [
  {
    id: 'product-ad',
    name: '产品广告',
    description: '经典 4 段式广告结构：吸引注意 → 痛点共鸣 → 产品方案 → 行动召唤',
    icon: '📦',
    category: 'ad',
    tags: ['广告', '产品', '营销'],
    duration: 10,
    segments: [
      { prompt: 'A person struggling with a messy desk, papers scattered everywhere, frustrated expression, cinematic lighting', duration: 3 },
      { prompt: 'Close-up of the same person looking tired and overwhelmed, dramatic shadows, shallow depth of field', duration: 2 },
      { prompt: 'Sleek modern desk organizer appearing with a magical glow, everything neatly arranged, bright and clean aesthetic', duration: 3 },
      { prompt: 'Happy person using the organized desk with a smile, warm natural lighting, professional workspace', duration: 2 },
    ],
    example: {
      title: '智能台灯广告',
      description: '展示一个困扰于暗光环境的用户，通过智能台灯解决问题，最终高效工作。',
      segments: [
        { prompt: 'A person working late at night under dim yellowish light, squinting at the screen, tired and strained, cinematic moody', duration: 3 },
        { prompt: 'Close-up of tired eyes and a frown in poor lighting, shadows across the face, dramatic', duration: 2 },
        { prompt: 'A sleek modern smart desk lamp turning on with a warm white glow, illuminating the workspace perfectly, product shot style', duration: 3 },
        { prompt: 'The same person now working comfortably under perfect lighting, focused and productive, bright and warm atmosphere', duration: 2 },
      ],
      thumbnailTip: '暗光困扰 → 智能台灯 → 高效工作',
    },
  },
  {
    id: 'short-drama',
    name: '短视频剧情',
    description: '5 段式微剧情：开场 → 铺垫 → 冲突 → 高潮 → 结局',
    icon: '🎬',
    category: 'drama',
    tags: ['剧情', '短视频', '故事'],
    duration: 10,
    segments: [
      { prompt: 'A young woman walking through a busy city street at dusk, neon lights reflecting on wet pavement, atmospheric', duration: 2 },
      { prompt: 'She notices a mysterious old bookshop she has never seen before, warm golden light spilling from the doorway, fantasy mood', duration: 2 },
      { prompt: 'Inside the bookshop, books floating in mid-air, glowing pages, magical atmosphere with particle effects', duration: 2 },
      { prompt: 'She reaches out to touch a glowing book, energy swirling around her hand, intense magical light', duration: 2 },
      { prompt: 'The woman standing in a vast beautiful library that appeared from the book, amazed expression, epic wide shot', duration: 2 },
    ],
    example: {
      title: '神秘书店',
      description: '女孩在下班路上发现一家神秘书店，翻开一本发光的书，进入了一个魔法图书馆。',
      segments: [
        { prompt: 'A young woman in office clothes walking alone on a rainy evening street, neon reflections, melancholy mood', duration: 2 },
        { prompt: 'She stops in front of a tiny old bookshop with a glowing sign that reads "Lost Stories", warm amber light from windows', duration: 2 },
        { prompt: 'Inside, ancient books hover in the air, pages turning by themselves, dust motes catching golden light, magical realism', duration: 2 },
        { prompt: 'Her fingers touch a book that pulses with blue light, energy cascading outward, dramatic close-up', duration: 2 },
        { prompt: 'She stands in an infinite magical library with floating bookshelves and aurora lights overhead, wonder on her face', duration: 2 },
      ],
      thumbnailTip: '雨夜独行 → 神秘书店 → 魔法之书 → 无限图书馆',
    },
  },
  {
    id: 'music-video',
    name: '音乐 MV',
    description: '4 段式 MV 结构：前奏 → 主歌 → 副歌 → 尾奏，适合配乐视频创作',
    icon: '🎵',
    category: 'mv',
    tags: ['MV', '音乐', '视觉'],
    duration: 10,
    segments: [
      { prompt: 'Silhouette of a dancer against a massive sunset, slow motion, lens flare, cinematic wide shot', duration: 3 },
      { prompt: 'The dancer moving fluidly through an empty warehouse, dramatic side lighting, dust particles in the air', duration: 2 },
      { prompt: 'Explosion of colorful powder and light surrounding the dancer in mid-air, high energy, vibrant colors, dynamic angle', duration: 3 },
      { prompt: 'The dancer standing still, head bowed, single spotlight fading out, intimate and emotional', duration: 2 },
    ],
    example: {
      title: '自由之舞',
      description: '舞者从日落到仓库，从沉静到爆发，用肢体语言诠释自由与释放。',
      segments: [
        { prompt: 'A lone dancer standing on a rooftop at golden hour, wind blowing through hair, epic city skyline behind, slow motion', duration: 3 },
        { prompt: 'Dancing in an abandoned factory with shafts of light coming through broken windows, contemporary movement', duration: 2 },
        { prompt: 'Water splashing around the dancer in slow motion, powerful leap, blue and white light, explosive energy', duration: 3 },
        { prompt: 'Dancer sitting on the rooftop edge at night, city lights below, quiet contemplation, breathing slowly', duration: 2 },
      ],
      thumbnailTip: '天台日落 → 工厂独舞 → 水中爆发 → 夜晚沉思',
    },
  },
  {
    id: 'tutorial',
    name: '教程演示',
    description: '3 段式教学结构：问题引入 → 操作演示 → 效果展示',
    icon: '📚',
    category: 'tutorial',
    tags: ['教程', '演示', '教学'],
    duration: 5,
    segments: [
      { prompt: 'A clean desk with a laptop showing a complicated software interface, person looking confused, soft office lighting', duration: 2 },
      { prompt: 'Close-up of the screen showing step-by-step cursor movements with highlighted UI elements, clean and minimal', duration: 2 },
      { prompt: 'The person smiling at the screen with the completed result visible, bright and satisfying atmosphere', duration: 1 },
    ],
    example: {
      title: 'AI 绘画入门',
      description: '展示 AI 绘画工具从安装到出图的全过程，适合教学类短视频。',
      segments: [
        { prompt: 'A blank digital canvas on screen with a question mark, clean dark UI, mysterious and inviting', duration: 2 },
        { prompt: 'Typing a text prompt into an AI art generator interface, words appearing with a typing animation, modern UI', duration: 2 },
        { prompt: 'A stunning AI-generated artwork appearing on screen with a flash of light, vibrant colors, wow factor', duration: 1 },
      ],
      thumbnailTip: '空白画布 → 输入提示词 → AI 生成作品',
    },
  },
  {
    id: 'brand-story',
    name: '品牌故事',
    description: '5 段式品牌叙事：起源 → 坚持 → 突破 → 价值 → 愿景',
    icon: '✨',
    category: 'brand',
    tags: ['品牌', '企业', '叙事'],
    duration: 10,
    segments: [
      { prompt: 'A small workshop with hand tools and raw materials, warm lamplight, craftsman working late, nostalgic and intimate', duration: 2 },
      { prompt: 'The craftsman facing challenges, broken pieces on the workbench, sweat on forehead, determined expression, dramatic', duration: 2 },
      { prompt: 'A breakthrough moment, the craftsman holding up a beautifully finished product, golden hour light streaming in', duration: 2 },
      { prompt: 'The product being used and enjoyed by people in various settings, montage style, warm and joyful', duration: 2 },
      { prompt: 'A modern brand showroom with the product line displayed elegantly, aspirational lifestyle, bright and premium', duration: 2 },
    ],
    example: {
      title: '手工皮具品牌',
      description: '从一间小作坊到品牌诞生，展现匠心精神与品质传承。',
      segments: [
        { prompt: 'A humble leather workshop, vintage tools laid out neatly, a pair of worn hands cutting leather by lamplight', duration: 2 },
        { prompt: 'Close-up of stitches being pulled tight, a needle breaking, the craftsman pausing with focused intensity', duration: 2 },
        { prompt: 'The first perfect leather bag sitting on the workbench, sunlight illuminating every detail, pride and relief', duration: 2 },
        { prompt: 'Different people carrying the bag in city streets, cafes, and galleries, lifestyle montage, warm tones', duration: 2 },
        { prompt: 'A minimalist brand store with the full collection displayed, evening light, premium and aspirational', duration: 2 },
      ],
      thumbnailTip: '小作坊 → 匠心坚持 → 突破之作 → 品牌愿景',
    },
  },
];

export function getTemplateById(id: string): StoryboardTemplate | undefined {
  return STORYBOARD_TEMPLATES.find((t) => t.id === id);
}

export function getTemplatesByCategory(category: string): StoryboardTemplate[] {
  return STORYBOARD_TEMPLATES.filter((t) => t.category === category);
}
