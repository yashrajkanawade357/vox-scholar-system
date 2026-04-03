import { useState, useEffect } from 'react';
import { 
  Bell, 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  MoreVertical,
  ShieldAlert,
  PhoneCall,
  Database
} from 'lucide-react';
import client from '../api/client';
import ThreatBadge from '../components/ThreatBadge';

const TABS = [
  { id: 'all', label: 'All Alerts' },
  { id: 'high', label: 'High' },
  { id: 'medium', label: 'Medium' },
  { id: 'low', label: 'Low' },
  { id: 'vox', label: 'VOX' },
  { id: 'scholar', label: 'Scholar' },
  { id: 'today', label: 'Today' },
];

export default function AlertCentre() {
  const [activeTab, setActiveTab] = useState('all');
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const response = await client.get(`/api/alerts?filter=${activeTab.toUpperCase()}&page=${page}`);
        setAlerts(response.alerts || []);
      } catch (err) {
        console.warn('API /api/alerts not found, using mock data');
        setAlerts([
          { id: 1, severity: 'HIGH', title: 'A.I. Voice Clone Detected', desc: 'Emergency relative scam pattern triggered from +1 405-293-1102.', source: 'VOX', time: '2 mins ago', status: 'Blocked' },
          { id: 2, severity: 'MEDIUM', title: 'Suspicious OTP Burst', desc: 'Rapid OTP requests (8+ in 60s) from unverified banking gateway.', source: 'Scholar', time: '14 mins ago', status: 'Monitoring' },
          { id: 3, severity: 'HIGH', title: 'Blacklisted Phishing Link', desc: 'User received message with known malicious domain: bank-verif.net.', source: 'Scholar', time: '41 mins ago', status: 'Blocked' },
          { id: 4, severity: 'LOW', title: 'Unusual Call Frequency', desc: 'Outbound call volume high for this contact ID. Mark for review.', source: 'VOX', time: '1h 12m ago', status: 'Logged' },
          { id: 5, severity: 'MEDIUM', title: 'Mimicked Sender ID', desc: 'Bank of America spoofed via unverified regional gateway.', source: 'Scholar', time: '2h 15m ago', status: 'Flagged' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [activeTab, page]);

  return (
    <div className="p-8 space-y-8 bg-bg-primary min-h-screen max-w-6xl mx-auto">
      {/* Header & Stats */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <h2 className="text-2xl font-black text-text-primary tracking-tighter uppercase italic">Alert Centre</h2>
          <p className="text-xs text-text-muted font-medium opacity-80 uppercase tracking-widest leading-none">Real-time fraud incident management</p>
        </div>
        <div className="flex items-center gap-3">
          {[
            { label: 'HIGH', count: 12, color: 'text-accent-red' },
            { label: 'MEDIUM', count: 28, color: 'text-accent-amber' },
            { label: 'LOW', count: 43, color: 'text-accent-green' },
            { label: 'SAFE', count: 1201, color: 'text-text-muted' },
          ].map((stat, i) => (
            <div key={i} className="bg-bg-card border border-border-custom px-4 py-2 rounded-xl flex items-center gap-2">
              <span className={`text-[10px] font-black ${stat.color}`}>{stat.label}:</span>
              <span className="text-xs font-bold text-text-primary italic">{stat.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="border-b border-border-custom flex items-center justify-between">
        <div className="flex overflow-x-auto no-scrollbar gap-8">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 text-[10px] font-black uppercase tracking-[0.2em] relative transition-all ${
                activeTab === tab.id ? 'text-accent-red' : 'text-text-muted hover:text-text-primary'
              }`}
            >
              {tab.label}
              {activeTab === tab.id && <span className="absolute bottom-0 left-0 w-full h-[2px] bg-accent-red" />}
            </button>
          ))}
        </div>
        <div className="hidden md:flex items-center gap-4 text-text-muted">
          <div className="relative group">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 opacity-40 group-focus-within:opacity-100 transition-opacity" />
            <input 
              type="text" 
              placeholder="Search alerts..." 
              className="bg-bg-card border border-border-custom px-10 py-2 rounded-xl text-xs font-medium focus:ring-1 focus:ring-accent-red transition-all w-48 focus:w-64" 
            />
          </div>
          <button className="bg-bg-card border border-border-custom p-2 rounded-xl hover:bg-bg-surface transition-all">
            <Filter size={14} />
          </button>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          Array(5).fill(0).map((_, i) => (
            <div key={i} className="h-24 bg-bg-card border border-border-custom rounded-2xl animate-pulse" />
          ))
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="group flex items-center gap-6 p-6 bg-bg-card rounded-2xl border border-border-custom hover:border-accent-red/20 hover:shadow-lg transition-all relative overflow-hidden">
              <div className={`absolute left-0 top-0 h-full w-1 ${
                alert.severity === 'HIGH' ? 'bg-accent-red' : 
                alert.severity === 'MEDIUM' ? 'bg-accent-amber' : 'bg-accent-green'
              }`} />
              
              <div className="flex flex-col gap-2 min-w-[140px]">
                <ThreatBadge level={alert.severity} />
                <div className="flex items-center gap-2 text-[10px] font-bold text-text-muted uppercase tracking-widest">
                  {alert.source === 'VOX' ? <PhoneCall size={10} className="text-accent-blue" /> : <Database size={10} className="text-[#9333ea]" />}
                  {alert.source} SYSTEM
                </div>
              </div>

              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-black text-text-primary tracking-tight mb-1 group-hover:text-accent-red transition-colors whitespace-nowrap overflow-hidden text-ellipsis">
                  {alert.title}
                </h4>
                <p className="text-[11px] text-text-muted italic leading-relaxed opacity-80 line-clamp-1">
                  {alert.desc}
                </p>
              </div>

              <div className="flex flex-col items-end gap-2 shrink-0">
                <span className="text-[10px] font-bold text-text-muted opacity-60 uppercase">{alert.time}</span>
                <span className={`px-2 py-0.5 rounded-[4px] text-[10px] font-black uppercase tracking-tighter border ${
                  alert.status === 'Blocked' ? 'bg-accent-red/10 text-accent-red border-accent-red/20' : 
                  'bg-accent-amber/10 text-accent-amber border-accent-amber/20'
                }`}>
                  {alert.status}
                </span>
              </div>

              <button className="bg-bg-primary/50 p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreVertical size={14} className="text-text-muted" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t border-border-custom pt-8 pb-16">
        <p className="text-[10px] font-bold text-text-muted uppercase tracking-[0.15em]">
          Showing 11 of <span className="text-text-primary font-black">1,284</span> alerts
        </p>
        <div className="flex items-center gap-2">
          <button className="bg-bg-card border border-border-custom p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-bg-surface transition-all disabled:opacity-30" disabled>
            <ChevronLeft size={16} />
          </button>
          {[1, 2, 3, '...', 117].map((n, i) => (
            <button 
              key={i} 
              onClick={() => typeof n === 'number' && setPage(n)}
              className={`min-w-[36px] h-9 rounded-xl border flex items-center justify-center text-[10px] font-black tracking-widest transition-all ${
                page === n ? 'bg-accent-red border-accent-red text-white' : 'bg-bg-card border-border-custom text-text-muted hover:border-text-primary'
              }`}
            >
              {n}
            </button>
          ))}
          <button 
            onClick={() => setPage(prev => prev + 1)}
            className="bg-bg-card border border-border-custom p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-bg-surface transition-all"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
