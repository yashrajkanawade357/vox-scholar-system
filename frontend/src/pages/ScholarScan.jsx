import { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { 
  FileSearch, 
  ShieldX, 
  Image as ImageIcon, 
  Key,
  ChevronRight
} from 'lucide-react';
import useWebSocket from '../hooks/useWebSocket';
import MetricCard from '../components/MetricCard';
import MessageItem from '../components/MessageItem';
import AnalysisPanel from '../components/AnalysisPanel';

const LINK_CHART_COLORS = ['#E24B4A', '#639922'];
const IMAGE_CHART_COLORS = ['#378ADD', '#9333ea'];

export default function ScholarScan() {
  const [messages, setMessages] = useState([
    { id: 1, sender: '+1 405-293-1102', time: '10:42 AM', text: 'URGENT: Your account has been suspended. Please click here to verify: http://bit.ly/secure-verif-291', severity: 'HIGH', linkStatus: 'PHISHING', linkDetails: 'bit.ly/secure-verif-291 (Blacklisted)', vtCount: '48/90', sbVerdict: 'MALICIOUS', indicators: ['Urgency language', 'Unofficial number', 'Mimics sender ID'] },
    { id: 2, sender: 'Bank of America', time: '09:12 AM', text: 'Your monthly statement is ready for viewing. Log in to your portal to download.', severity: 'SAFE', linkStatus: 'SAFE', linkDetails: 'bankofamerica.com (Verified)', vtCount: '0/90', sbVerdict: 'CLEAN', indicators: ['Verified Sender'] },
    { id: 3, sender: 'Unknown #221', time: '08:45 AM', text: 'Hey, I sent the picture we talked about. Check it out!', severity: 'MEDIUM', linkStatus: 'SAFE', linkDetails: 'No links present', vtCount: '0/90', sbVerdict: 'N/A', indicators: ['Unknown Sender', 'Potential OSINT match'] },
  ]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const { lastMessage } = useWebSocket('scholar');

  // Listen for new messages via WebSocket
  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [lastMessage, ...prev].slice(0, 50));
    }
  }, [lastMessage]);

  const stats = [
    { icon: FileSearch, label: 'Msgs Scanned', value: '9,130', sub: '+412 today', color: 'blue' },
    { icon: ShieldX, label: 'Links Blocked', value: '247', sub: '12.4% rate', color: 'red' },
    { icon: ImageIcon, label: 'Images Checked', value: '512', sub: 'Deepfake analysis', color: 'purple' },
    { icon: Key, label: 'OTPs Analysed', value: '1,841', sub: 'Fraud protection', color: 'amber' },
  ];

  const linkScanData = [
    { name: 'Phishing', value: 142 },
    { name: 'Safe', value: 890 },
  ];

  const imageDetectionData = [
    { name: 'Deepfake', value: 24 },
    { name: 'Authentic', value: 488 },
  ];

  return (
    <div className="flex flex-col h-full bg-bg-primary overflow-hidden">
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-8 pb-4">
        {stats.map((stat, i) => (
          <MetricCard key={i} {...stat} />
        ))}
      </div>

      {/* Main Two-Panel Section */}
      <div className="flex-1 flex gap-8 p-8 py-4 overflow-hidden">
        {/* Left: Feed (40%) */}
        <div className="w-[40%] flex flex-col min-w-0">
          <div className="flex items-center justify-between mb-4 px-2">
            <h3 className="text-[10px] font-black text-text-muted uppercase tracking-[0.2em] flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-red animate-pulse" />
              Live Incoming Feed
            </h3>
            <span className="text-[9px] text-text-muted font-bold opacity-60 uppercase tracking-widest leading-none">Showing Latest 50</span>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-1">
            {messages.map(msg => (
              <MessageItem 
                key={msg.id} 
                message={msg} 
                isActive={selectedMessage?.id === msg.id}
                onClick={() => setSelectedMessage(msg)}
              />
            ))}
          </div>
        </div>

        {/* Right: Analysis (60%) */}
        <div className="w-[60%] flex flex-col min-w-0">
          <AnalysisPanel message={selectedMessage} />
        </div>
      </div>

      {/* Bottom Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8 pt-4">
        <div className="bg-bg-card rounded-2xl border border-border-custom p-6">
          <h3 className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-6">Link Scan Results Today</h3>
          <div className="h-[120px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={linkScanData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} axisLine={false} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={9} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: '10px' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={40}>
                  {linkScanData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={LINK_CHART_COLORS[index]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-bg-card rounded-2xl border border-border-custom p-6">
          <h3 className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-6">Image/Deepfake Detection</h3>
          <div className="h-[120px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={imageDetectionData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} axisLine={false} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={9} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111318', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: '10px' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={40}>
                  {imageDetectionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={IMAGE_CHART_COLORS[index]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
