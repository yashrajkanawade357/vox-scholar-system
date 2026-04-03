import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const pageTitles = {
  '/': 'Dashboard Overview',
  '/monitor': 'VOX Live Monitor',
  '/scholar': 'Scholar Scan Results',
  '/alerts': 'Security Alert Centre',
  '/reports': 'Incident Reports',
  '/settings': 'System Settings',
};

export default function Topbar() {
  const location = useLocation();
  const [syncTime, setSyncTime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSyncTime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Reset sync time when page changes
  useEffect(() => {
    setSyncTime(0);
  }, [location.pathname]);

  return (
    <header className="h-16 px-8 border-b border-border-custom/50 flex items-center justify-between bg-bg-primary/80 backdrop-blur-md sticky top-0 z-10">
      <h1 className="text-lg font-bold text-text-primary tracking-tight">
        {pageTitles[location.pathname] || 'System Control'}
      </h1>
      
      <div className="flex items-center space-x-6 text-[10px] font-bold uppercase tracking-widest">
        <div className="flex items-center text-accent-green">
          <span className="h-1.5 w-1.5 rounded-full bg-accent-green mr-2 shadow-[0_0_8px_#639922]"></span>
          All Systems Operational
        </div>
        <div className="text-text-muted">
          Last synced {syncTime}s ago
        </div>
      </div>
    </header>
  );
}
