export function Logo() {
  return (
    <div className="relative w-8 h-8 flex items-center justify-center">
      <div className="absolute inset-0 border border-[var(--text-tertiary)] rounded-lg" />
      <span className="text-sm font-bold text-[var(--text-primary)] relative z-10">U</span>
      <div className="absolute bottom-1 left-1 right-1 h-0.5 bg-[var(--text-tertiary)]" />
    </div>
  );
}

export function LogoLarge() {
  return (
    <div className="relative w-16 h-16 flex items-center justify-center">
      <div className="absolute inset-0 border-2 border-[var(--text-secondary)] rounded-xl" />
      <span className="text-3xl font-bold text-[var(--text-primary)] relative z-10">U</span>
      <div className="absolute bottom-2 left-2 right-2 h-1 bg-[var(--text-secondary)] rounded-full" />
    </div>
  );
}
