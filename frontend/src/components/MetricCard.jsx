export default function MetricCard({ icon: Icon, label, value, sub, color = 'blue' }) {
  const colorMap = {
    red: 'text-accent-red bg-accent-red/10 border-accent-red/20',
    blue: 'text-accent-blue bg-accent-blue/10 border-accent-blue/20',
    purple: 'text-[#9333ea] bg-[#9333ea]/10 border-[#9333ea]/20',
    green: 'text-accent-green bg-accent-green/10 border-accent-green/20',
    amber: 'text-accent-amber bg-accent-amber/10 border-accent-amber/20',
  };

  const selectedColor = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-bg-card p-5 rounded-2xl border border-border-custom hover:border-text-muted/30 transition-all flex flex-col justify-between h-32 group">
      <div className="flex items-center justify-between">
        <div className={`p-2 rounded-xl border ${selectedColor}`}>
          <Icon size={18} />
        </div>
        <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">{label}</span>
      </div>
      
      <div className="mt-4">
        <h3 className="text-2xl font-black text-text-primary tracking-tight">{value}</h3>
        <p className={`text-[10px] font-bold mt-0.5 ${sub.includes('↑') || sub.includes('+') ? 'text-accent-green' : 'text-text-muted opacity-80'}`}>
          {sub}
        </p>
      </div>
    </div>
  );
}

export function MetricCardSkeleton() {
  return (
    <div className="bg-bg-card p-5 rounded-2xl border border-border-custom h-32 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="h-9 w-9 bg-border-custom rounded-xl" />
        <div className="h-3 w-16 bg-border-custom rounded" />
      </div>
      <div className="mt-6">
        <div className="h-6 w-24 bg-border-custom rounded mb-2" />
        <div className="h-3 w-32 bg-border-custom rounded" />
      </div>
    </div>
  );
}
