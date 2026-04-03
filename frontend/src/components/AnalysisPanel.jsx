import { ShieldCheck, ShieldAlert, Globe, ExternalLink, UserMinus, AlertTriangle, CheckCircle } from 'lucide-react';
import client from '../api/client';

export default function AnalysisPanel({ message }) {
  if (!message) {
    return (
      <div className="h-full flex items-center justify-center text-text-muted italic text-xs animate-pulse bg-bg-card/30 rounded-2xl border border-border-custom border-dashed">
        Select a message from the feed to analyze threat vectors...
      </div>
    );
  }

  const handleAction = async (action) => {
    try {
      if (action === 'block') await client.post('/api/block', { sender: message.sender });
      if (action === 'report') await client.post('/api/report', { message_id: message.id });
      alert(`Action ${action} successful for ${message.sender}`);
    } catch (err) {
      console.error(`Failed to ${action}:`, err);
    }
  };

  return (
    <div className="bg-bg-card rounded-2xl border border-border-custom p-8 h-full flex flex-col overflow-y-auto">
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-border-custom/50">
        <div>
          <h2 className="text-xl font-black text-text-primary uppercase tracking-tighter">{message.sender}</h2>
          <p className="text-[10px] text-text-muted mt-1 uppercase tracking-widest font-bold">{message.time} · Trace ID: #SK-{message.id}</p>
        </div>
        <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 ${
          message.severity === 'HIGH' ? 'bg-accent-red/10 border-accent-red/20 text-accent-red' : 'bg-accent-green/10 border-accent-green/20 text-accent-green'
        }`}>
          {message.severity === 'HIGH' ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
          <span className="text-xs font-black uppercase tracking-widest">{message.severity} THREAT</span>
        </div>
      </div>

      <div className="mb-8 p-6 bg-bg-primary/50 rounded-xl border border-white/5 ring-1 ring-white/5">
        <p className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap font-medium">
          {message.text}
        </p>
      </div>

      {/* Link Scan Result */}
      <div className="mb-8">
        <h3 className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-4 flex items-center gap-2">
          <Globe size={12} /> Link Analysis Results
        </h3>
        <div className={`p-5 rounded-2xl border flex items-center justify-between ${
          message.linkStatus === 'PHISHING' ? 'bg-accent-red/5 border-accent-red/20' : 'bg-accent-green/5 border-accent-green/20'
        }`}>
          <div className="flex items-center gap-4">
            <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
              message.linkStatus === 'PHISHING' ? 'text-accent-red' : 'text-accent-green'
            }`}>
              {message.linkStatus === 'PHISHING' ? <ShieldAlert size={28} /> : <ShieldCheck size={28} />}
            </div>
            <div>
              <p className={`text-xs font-black leading-none uppercase tracking-tighter ${
                message.linkStatus === 'PHISHING' ? 'text-accent-red' : 'text-accent-green'
              }`}>
                {message.linkStatus === 'PHISHING' ? '✗ PHISHING URL DETECTED' : '✓ SAFE LINK'}
              </p>
              <p className="text-[10px] text-text-muted mt-1.5 font-bold uppercase tracking-widest opacity-60">
                {message.linkDetails || 'No malicious links found in content body.'}
              </p>
            </div>
          </div>
          <div className="text-[10px] font-black text-text-muted uppercase tracking-widest flex flex-col items-end gap-1.5">
            <span className="opacity-80">VIRUSTOTAL: {message.vtCount || '0/90'} FLAGS</span>
            <span className="opacity-80">SAFEBROWSING: {message.sbVerdict || 'CLEAN'}</span>
          </div>
        </div>
      </div>

      {/* Indicators */}
      <div className="mb-8">
        <h3 className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-4 flex items-center gap-2">
          <AlertTriangle size={12} /> Fraud Indicators
        </h3>
        <div className="flex flex-wrap gap-2">
          {message.indicators?.map((indicator, idx) => (
            <span key={idx} className="bg-bg-primary border border-border-custom px-3 py-1.5 rounded-full text-[10px] font-bold text-text-muted uppercase tracking-tighter flex items-center gap-1.5">
              <span className="h-1 w-1 rounded-full bg-accent-amber" />
              {indicator}
            </span>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-auto pt-8 border-t border-border-custom/50 flex items-center gap-4">
        <button 
          onClick={() => handleAction('block')}
          className="flex-1 bg-accent-red/10 border border-accent-red/20 text-accent-red py-3 rounded-xl text-[11px] font-black uppercase tracking-widest hover:bg-accent-red hover:text-white transition-all flex items-center justify-center gap-2"
        >
          <UserMinus size={14} /> Block Sender
        </button>
        <button 
          onClick={() => handleAction('report')}
          className="flex-1 bg-accent-amber/10 border border-accent-amber/20 text-accent-amber py-3 rounded-xl text-[11px] font-black uppercase tracking-widest hover:bg-accent-amber hover:text-white transition-all flex items-center justify-center gap-2"
        >
          <AlertTriangle size={14} /> Report Fraud
        </button>
        <button 
          className="flex-1 bg-accent-green/10 border border-accent-green/20 text-accent-green py-3 rounded-xl text-[11px] font-black uppercase tracking-widest hover:bg-accent-green hover:text-white transition-all flex items-center justify-center gap-2"
        >
          <CheckCircle size={14} /> Mark Safe
        </button>
      </div>
    </div>
  );
}
