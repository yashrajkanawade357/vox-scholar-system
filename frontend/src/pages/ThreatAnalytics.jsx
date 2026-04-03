import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { 
  Scale, 
  Gavel, 
  Fingerprint, 
  Building2, 
  FileText, 
  AlertCircle 
} from 'lucide-react';

const TREND_DATA = [
  { month: 'Apr', vox: 420, scholar: 850, total: 1270 },
  { month: 'May', vox: 380, scholar: 920, total: 1300 },
  { month: 'Jun', vox: 510, scholar: 880, total: 1390 },
  { month: 'Jul', vox: 450, scholar: 910, total: 1360 },
  { month: 'Aug', vox: 580, scholar: 1040, total: 1620 },
  { month: 'Sep', vox: 620, scholar: 1110, total: 1730 },
  { month: 'Oct', vox: 540, scholar: 980, total: 1520 },
  { month: 'Nov', vox: 490, scholar: 1020, total: 1510 },
  { month: 'Dec', vox: 710, scholar: 1250, total: 1960 },
  { month: 'Jan', vox: 640, scholar: 1180, total: 1820 },
  { month: 'Feb', vox: 590, scholar: 1090, total: 1680 },
  { month: 'Mar', vox: 680, scholar: 1210, total: 1890 },
];

const DAY_DATA = [
  { day: 'Mon', count: 480 },
  { day: 'Tue', count: 520 },
  { day: 'Wed', count: 450 },
  { day: 'Thu', count: 410 },
  { day: 'Fri', count: 590 },
  { day: 'Sat', count: 320 },
  { day: 'Sun', count: 280 },
];

const HOUR_DATA = [
  { time: '00-04', count: 120 },
  { time: '04-08', count: 180 },
  { time: '08-12', count: 540 },
  { time: '12-16', count: 720 },
  { time: '16-20', count: 680 },
  { time: '20-00', count: 310 },
];

const CHANNEL_DATA = [
  { channel: 'SMS', count: 480 },
  { channel: 'WhatsApp', count: 310 },
  { channel: 'Call', count: 270 },
  { channel: 'Email', count: 195 },
  { channel: 'Other', count: 69 },
];

const KG_STATS = [
  { icon: Gavel, label: 'Law Nodes', value: '4,821', color: 'blue' },
  { icon: Scale, label: 'Rule Edges', value: '12,340', color: 'purple' },
  { icon: Fingerprint, label: 'Fraud Patterns', value: '983', color: 'red' },
  { icon: Building2, label: 'Bank Policies', value: '621', color: 'amber' },
  { icon: FileText, label: 'IPC Sections', value: '312', color: 'green' },
  { icon: AlertCircle, label: 'CERT-In Alerts', value: '154', color: 'red' },
];

export default function ThreatAnalytics() {
  return (
    <div className="p-8 pb-16 space-y-8 bg-bg-primary min-h-screen">
      {/* Annual Trend LineChart */}
      <div className="bg-bg-card rounded-2xl border border-border-custom p-8 shadow-sm">
        <h3 className="text-sm font-black uppercase tracking-[0.2em] mb-8 text-text-primary flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-accent-blue shadow-[0_0_8px_#378ADD]" />
          Annual Detection Trend
        </h3>
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={TREND_DATA}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" stroke="#6B7280" fontSize={11} axisLine={false} tickLine={false} />
              <YAxis stroke="#6B7280" fontSize={11} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#161A21', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: '11px' }}
              />
              <Legend verticalAlign="top" align="right" iconType="circle" />
              <Line type="monotone" dataKey="vox" stroke="#378ADD" strokeWidth={3} dot={{ fill: '#378ADD', strokeWidth: 2 }} name="VOX Blocked" />
              <Line type="monotone" dataKey="scholar" stroke="#9333ea" strokeWidth={3} dot={{ fill: '#9333ea', strokeWidth: 2 }} name="Scholar Blocked" />
              <Line type="monotone" dataKey="total" stroke="#E24B4A" strokeWidth={3} dot={{ fill: '#E24B4A', strokeWidth: 2 }} name="Total Threats" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Main BarCharts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Day of Week */}
        <div className="bg-bg-card rounded-2xl border border-border-custom p-8">
          <h3 className="text-[10px] font-black uppercase tracking-widest mb-6 text-text-muted italic">Threats by Day of Week</h3>
          <div className="h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DAY_DATA}>
                <XAxis dataKey="day" stroke="#6B7280" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={10} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', fontSize: '10px' }} />
                <Bar dataKey="count" fill="#378ADD" radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hour of Day */}
        <div className="bg-bg-card rounded-2xl border border-border-custom p-8">
          <h3 className="text-[10px] font-black uppercase tracking-widest mb-6 text-text-muted italic">Threats by Hour of Day</h3>
          <div className="h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={HOUR_DATA}>
                <XAxis dataKey="time" stroke="#6B7280" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={10} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', fontSize: '10px' }} />
                <Bar dataKey="count" fill="#BA7517" radius={[4, 4, 0, 0]} barSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Threats by Channel & KG Stats Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Channel BarChart */}
        <div className="lg:col-span-5 bg-bg-card rounded-2xl border border-border-custom p-8">
          <h3 className="text-[10px] font-black uppercase tracking-widest mb-6 text-text-muted italic">Threats by Channel</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={CHANNEL_DATA} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="channel" type="category" stroke="#F0F2F5" fontSize={11} axisLine={false} tickLine={false} width={80} />
                <Tooltip contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', fontSize: '10px' }} />
                <Bar dataKey="count" fill="#8884d8" radius={[0, 4, 4, 0]} barSize={24}>
                  {CHANNEL_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={['#378ADD', '#25D366', '#E24B4A', '#BA7517', '#6B7280'][index % 5]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* KG Stats Grid */}
        <div className="lg:col-span-7 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {KG_STATS.map((stat, i) => (
              <div key={i} className="bg-bg-card border border-border-custom rounded-2xl p-5 hover:border-text-muted/30 transition-all">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-4 ${
                  stat.color === 'red' ? 'bg-accent-red/10 text-accent-red' :
                  stat.color === 'blue' ? 'bg-accent-blue/10 text-accent-blue' :
                  stat.color === 'purple' ? 'bg-[#9333ea]/10 text-[#9333ea]' :
                  stat.color === 'green' ? 'bg-accent-green/10 text-accent-green' :
                  'bg-accent-amber/10 text-accent-amber'
                }`}>
                  <stat.icon size={16} />
                </div>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-widest mb-1">{stat.label}</p>
                <p className="text-xl font-black text-text-primary tracking-tighter">{stat.value}</p>
              </div>
            ))}
          </div>
          <div className="bg-bg-surface border border-border-custom rounded-2xl p-6">
            <h4 className="text-[10px] font-black text-text-primary uppercase tracking-[0.2em] mb-2">Legal Knowledge Graph Meta</h4>
            <p className="text-[10px] leading-relaxed text-text-muted font-medium italic opacity-80">
              Trained on RBI Rules, IPC Sections, Bank Policies, I4C Advisories, CERT-In Reports. 
              Graph indexing updated every 24 hours via automated legal crawling scripts.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
