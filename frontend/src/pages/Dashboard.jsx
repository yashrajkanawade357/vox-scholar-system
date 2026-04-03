import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  PhoneCall, 
  Database, 
  Zap, 
  ArrowRight,
  MonitorCheck,
  CheckCircle2,
  RefreshCcw
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart, 
  Pie, 
  Cell,
  Legend
} from 'recharts';
import client from '../api/client';
import MetricCard, { MetricCardSkeleton } from '../components/MetricCard';
import AlertItem, { AlertItemSkeleton } from '../components/AlertItem';

const BAR_COLORS = ['#E24B4A', '#378ADD', '#9333ea', '#639922', '#BA7517', '#6B7280'];
const PIE_COLORS = ['#E24B4A', '#378ADD', '#9333ea', '#639922', '#6B7280'];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [syncSeconds, setSyncSeconds] = useState(2);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Attempt to fetch live data
        const data = await client.get('/api/stats');
        setStats(data);
      } catch (err) {
        // Fallback to mock data from the spec
        console.warn('API /api/stats not found, using spec mock data');
        setStats({
          metrics: [
            { id: 1, icon: ShieldAlert, label: 'Threats Blocked', value: '1,284', sub: '+12 today', color: 'red' },
            { id: 2, icon: PhoneCall, label: 'Calls Screened', value: '3,672', sub: 'by VOX today', color: 'blue' },
            { id: 3, icon: Database, label: 'Msgs Analysed', value: '9,130', sub: 'by Scholar today', color: 'purple' },
            { id: 4, icon: Zap, label: 'Safe Score', value: '97.4%', sub: '↑ 0.3% this week', color: 'green' },
          ],
          threatsByType: [
            { name: 'Phishing', value: 520 },
            { name: 'Voice Scam', value: 310 },
            { name: 'Deepfake', value: 180 },
            { name: 'Malware', value: 140 },
            { name: 'OTP Fraud', value: 95 },
            { name: 'Other', value: 39 },
          ],
          attackDistribution: [
            { name: 'Phishing', value: 41 },
            { name: 'Voice', value: 24 },
            { name: 'Deepfake', value: 14 },
            { name: 'Malware', value: 11 },
            { name: 'Other', value: 10 },
          ],
          recentAlerts: [
            { id: 1, caller: '+1 405-293-1102', timestamp: '2 mins ago', severity: 'HIGH', status: 'Blocked', summary: 'Emergency relative scam pattern (A.I. Voice Clone detected)' },
            { id: 2, caller: 'Unknown (Private)', timestamp: '15 mins ago', severity: 'MEDIUM', status: 'Monitoring', summary: 'Unusual rapid-fire OTP request heuristic triggered.' },
            { id: 3, caller: 'Amazon Support (Spoofed)', timestamp: '42 mins ago', severity: 'HIGH', status: 'Blocked', summary: 'Social engineering script - Refund claim detected.' },
            { id: 4, caller: 'WhatsApp #2910', timestamp: '1h 12m ago', severity: 'LOW', status: 'Logged', summary: 'Standard promotional spam filtering.' },
          ]
        });
      } finally {
        setTimeout(() => setLoading(false), 800); // Small delay to show off skeletons
      }
    };

    fetchData();

    const syncTimer = setInterval(() => {
      setSyncSeconds(prev => (prev >= 60 ? 0 : prev + 1));
    }, 1000);

    return () => clearInterval(syncTimer);
  }, []);

  return (
    <div className="flex flex-col min-h-full">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 p-8">
        {loading ? (
          Array(4).fill(0).map((_, i) => <MetricCardSkeleton key={i} />)
        ) : (
          stats?.metrics.map(metric => <MetricCard key={metric.id} {...metric} />)
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 px-8 mb-8">
        {/* Bar Chart */}
        <div className="lg:col-span-7 bg-bg-card rounded-2xl border border-border-custom p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-text-muted">Threats Blocked by Type</h3>
            <div className="h-2 w-2 rounded-full bg-accent-red animate-pulse" />
          </div>
          <div className="h-[300px]">
            {loading ? (
              <div className="w-full h-full bg-border-custom/20 rounded-xl animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats?.threatsByType} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" stroke="#6B7280" fontSize={10} axisLine={false} tickLine={false} />
                  <YAxis dataKey="name" type="category" stroke="#F0F2F5" fontSize={10} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161A21', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}
                    itemStyle={{ color: '#F0F2F5', fontSize: '10px' }}
                  />
                  <Bar dataKey="value" fill="#E24B4A" radius={[0, 4, 4, 0]} barSize={20}>
                    {stats?.threatsByType.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Pie Chart */}
        <div className="lg:col-span-5 bg-bg-card rounded-2xl border border-border-custom p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-text-muted">Attack Distribution</h3>
            <ArrowRight size={14} className="text-text-muted" />
          </div>
          <div className="h-[300px]">
            {loading ? (
              <div className="w-full h-full bg-border-custom/20 rounded-xl animate-pulse" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats?.attackDistribution}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {stats?.attackDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161A21', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px' }}
                    itemStyle={{ color: '#F0F2F5', fontSize: '10px' }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    iconType="circle"
                    formatter={(value, entry) => <span className="text-[10px] text-text-muted font-medium ml-1">{value} ({entry.payload.value}%)</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Recent Alerts Section */}
      <div className="px-8 pb-8">
        <div className="bg-bg-card rounded-2xl border border-border-custom overflow-hidden">
          <div className="p-6 border-b border-border-custom flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="text-accent-amber" size={18} />
              <h3 className="text-sm font-black uppercase tracking-tight text-text-primary">Recent Monitoring Alerts</h3>
            </div>
            <Link to="/alerts" className="text-xs font-bold text-accent-blue hover:underline flex items-center gap-1 transition-all">
              View All <ArrowRight size={12} />
            </Link>
          </div>
          <div className="flex flex-col">
            {loading ? (
              Array(4).fill(0).map((_, i) => <AlertItemSkeleton key={i} />)
            ) : (
              stats?.recentAlerts.map(alert => <AlertItem key={alert.id} alert={alert} />)
            )}
          </div>
        </div>
      </div>

      {/* Bottom Status Bar */}
      <footer className="mt-auto h-10 bg-bg-surface border-t border-border-custom/50 px-8 flex items-center justify-between text-[9px] font-black uppercase tracking-[0.2em]">
        <div className="flex items-center space-x-6">
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-green" />
            <span className="text-text-primary">VOX Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-green" />
            <span className="text-text-primary">Scholar Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-1.5 w-1.5 rounded-full bg-accent-blue shadow-[0_0_8px_#378ADD]" />
            <span className="text-text-primary">Graph DB Synced</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-text-muted">
          <RefreshCcw size={10} className={`${syncSeconds % 5 === 0 ? 'animate-spin' : ''}`} />
          Last Sync {syncSeconds}s ago
        </div>
      </footer>
    </div>
  );
}
