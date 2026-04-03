import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Mic2, 
  Search, 
  Bell, 
  FileText, 
  Settings as SettingsIcon 
} from 'lucide-react';
import LiveBadge from './LiveBadge';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Mic2, label: 'VOX Monitor', path: '/monitor' },
  { icon: Search, label: 'Scholar Scan', path: '/scholar' },
  { icon: Bell, label: 'Alerts', path: '/alerts' },
  { icon: FileText, label: 'Reports', path: '/reports' },
  { icon: SettingsIcon, label: 'Settings', path: '/settings' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-[180px] h-screen bg-bg-surface border-r border-border-custom flex flex-col flex-shrink-0 transition-all">
      <div className="p-4 mb-4">
        <h2 className="text-xl font-black text-accent-red tracking-tighter leading-none">BIGDADDY</h2>
        <p className="text-[10px] text-text-muted mt-1 font-medium uppercase tracking-widest opacity-80">AI Fraud Detection</p>
      </div>

      <nav className="flex-1 px-2 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-3 py-2.5 transition-all relative group ${
                isActive
                  ? 'bg-accent-red/5 text-accent-red border-l-[3px] border-accent-red pl-[9px]'
                  : 'text-text-muted hover:bg-bg-card hover:text-text-primary border-l-[3px] border-transparent'
              }`}
            >
              <item.icon size={18} className={`${isActive ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'}`} />
              <span className="text-xs font-semibold tracking-wide">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto border-t border-border-custom/50">
        <LiveBadge />
      </div>
    </aside>
  );
}
