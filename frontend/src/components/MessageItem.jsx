import ThreatBadge from './ThreatBadge';

export default function MessageItem({ message, isActive, onClick }) {
  const getBorderColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': return 'border-accent-red';
      case 'medium': return 'border-accent-amber';
      case 'safe': return 'border-accent-green';
      default: return 'border-transparent';
    }
  };

  return (
    <div 
      onClick={onClick}
      className={`p-4 border-l-4 cursor-pointer transition-all hover:bg-bg-card/80 mb-2 rounded-r-lg ${getBorderColor(message.severity)} ${
        isActive ? 'bg-bg-card shadow-lg ring-1 ring-white/5' : 'bg-transparent opacity-80'
      }`}
    >
      <div className="flex justify-between items-start mb-1">
        <span className="text-xs font-black text-text-primary uppercase tracking-tighter truncate max-w-[120px]">
          {message.sender}
        </span>
        <span className="text-[9px] text-text-muted font-bold">{message.time}</span>
      </div>
      <p className="text-[11px] text-text-muted line-clamp-2 leading-relaxed mb-2">
        {message.text}
      </p>
      <div className="flex justify-end">
        <ThreatBadge level={message.severity} />
      </div>
    </div>
  );
}
