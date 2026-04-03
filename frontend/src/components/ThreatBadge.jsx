export default function ThreatBadge({ level }) {
  const getColors = () => {
    switch (level?.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'bg-accent-red/10 text-accent-red border-accent-red/20';
      case 'medium':
        return 'bg-accent-amber/10 text-accent-amber border-accent-amber/20';
      case 'low':
        return 'bg-accent-green/10 text-accent-green border-accent-green/20';
      default:
        return 'bg-bg-card text-text-muted border-border-custom';
    }
  };

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${getColors()}`}>
      {level || 'Unknown'}
    </span>
  );
}
