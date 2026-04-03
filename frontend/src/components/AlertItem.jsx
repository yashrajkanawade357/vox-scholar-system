import ThreatBadge from './ThreatBadge';

export default function AlertItem({ alert }) {
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'blocked': return 'text-accent-red bg-accent-red/10 border-accent-red/20';
      case 'monitoring': return 'text-accent-amber bg-accent-amber/10 border-accent-amber/20';
      case 'logged': return 'text-text-muted bg-bg-card border-border-custom';
      default: return 'text-text-muted bg-bg-card border-border-custom';
    }
  };

  return (
    <div className="flex items-center gap-6 py-4 border-b border-border-custom/40 last:border-0 hover:bg-bg-surface/50 px-4 transition-all group">
      <div className="flex flex-col min-w-[120px]">
        <span className="text-xs font-bold text-text-primary tracking-tight truncate">{alert.caller || 'Unknown'}</span>
        <span className="text-[10px] text-text-muted font-medium mt-0.5">{alert.timestamp || 'Just Now'}</span>
      </div>

      <div className="flex-1 flex items-center gap-3">
        <ThreatBadge level={alert.severity || alert.threatLevel} />
        <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-black uppercase tracking-tighter border ${getStatusColor(alert.status)}`}>
          {alert.status || 'Pending'}
        </span>
      </div>

      <div className="text-[10px] text-text-muted font-medium italic opacity-60 group-hover:opacity-100 transition-opacity max-w-[200px] truncate">
        {alert.summary || 'Triggered heuristic scam pattern detection...'}
      </div>

      <button className="text-[10px] font-bold text-accent-blue hover:text-[#5fa9f2] uppercase tracking-widest ml-auto">
        Details →
      </button>
    </div>
  );
}

export function AlertItemSkeleton() {
  return (
    <div className="flex items-center gap-6 py-4 px-4 animate-pulse border-b border-border-custom/40">
      <div className="w-[120px]">
        <div className="h-3 w-20 bg-border-custom rounded mb-1" />
        <div className="h-2 w-14 bg-border-custom rounded" />
      </div>
      <div className="flex gap-2">
        <div className="h-4 w-12 bg-border-custom rounded" />
        <div className="h-4 w-16 bg-border-custom rounded" />
      </div>
      <div className="h-3 w-40 bg-border-custom rounded mx-4" />
      <div className="h-3 w-10 bg-border-custom rounded ml-auto" />
    </div>
  );
}
