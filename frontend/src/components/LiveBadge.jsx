export default function LiveBadge() {
  return (
    <div className="flex items-center space-x-2">
      <div className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-red opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-red"></span>
      </div>
      <span className="text-[10px] font-black uppercase tracking-[0.2em] text-accent-red">Live</span>
    </div>
  );
}
