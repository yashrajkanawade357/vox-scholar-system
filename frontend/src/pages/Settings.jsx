import { useState } from 'react';
import { 
  User, 
  Mic2, 
  Search, 
  ShieldCheck, 
  Bell, 
  Database, 
  Info,
  Save,
  RotateCcw,
  CheckCircle2
} from 'lucide-react';
import client from '../api/client';

const SETTINGS_TABS = [
  { id: 'profile', icon: User, label: 'Profile' },
  { id: 'vox', icon: Mic2, label: 'VOX Settings' },
  { id: 'scholar', icon: Search, label: 'Scholar Settings' },
  { id: 'privacy', icon: ShieldCheck, label: 'Privacy & Zero Trust' },
  { id: 'notifications', icon: Bell, label: 'Notifications' },
  { id: 'kb', icon: Database, label: 'Legal Knowledge Base' },
  { id: 'about', icon: Info, label: 'About' },
];

export default function Settings() {
  const [activeTab, setActiveTab] = useState('vox');
  const [sensitivity, setSensitivity] = useState(72);
  const [saving, setSaving] = useState(false);
  
  const [toggles, setToggles] = useState({
    monitoring: true,
    cloneDetection: true,
    deepfakeDetection: false,
    autoBlock: true,
    multilingual: true,
  });

  const handleToggle = (key) => {
    setToggles(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await client.post('/api/settings', { toggles, sensitivity });
      alert('Settings saved successfully!');
    } catch (err) {
      console.error('Failed to save settings:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <header className="mb-10">
        <h2 className="text-2xl font-black text-text-primary tracking-tighter uppercase italic">System Settings</h2>
        <p className="text-xs text-text-muted mt-1 font-medium uppercase tracking-[0.2em] opacity-80">Configure AI detection and privacy parameters</p>
      </header>

      <div className="flex-1 flex gap-12 overflow-hidden pb-12">
        {/* Left Nav */}
        <aside className="w-64 space-y-1">
          {SETTINGS_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all text-xs font-bold uppercase tracking-widest ${
                activeTab === tab.id 
                  ? 'bg-accent-red text-white shadow-lg shadow-accent-red/20' 
                  : 'text-text-muted hover:bg-bg-card hover:text-text-primary'
              }`}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </aside>

        {/* Right Content */}
        <main className="flex-1 bg-bg-card rounded-3xl border border-border-custom p-10 overflow-y-auto custom-scrollbar">
          {activeTab === 'vox' && (
            <div className="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
              <section>
                <h3 className="text-sm font-black text-text-primary uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-accent-red" />
                  VOX Detection Parameters
                </h3>
                
                <div className="space-y-6">
                  {[
                    { id: 'monitoring', label: 'Real-time Call Monitoring', desc: 'Encrypted analysis of live voice data streams.' },
                    { id: 'cloneDetection', label: 'Voice Clone Detection', desc: 'Identifies A.I. synthesized voice patterns.' },
                    { id: 'deepfakeDetection', label: 'Deepfake Video Detection', desc: 'Analyses visual artifacts in video calls.', badge: 'Beta' },
                    { id: 'autoBlock', label: 'Auto-block High Risk Calls', desc: 'Instantly terminates calls with >95% scam probability.' },
                    { id: 'multilingual', label: 'Multilingual Support', desc: 'Detection for region-specific dialects.', badge: '9 languages' },
                  ].map((item) => (
                    <div key={item.id} className="flex items-center justify-between group">
                      <div className="pr-8">
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-bold text-text-primary uppercase tracking-tight">{item.label}</span>
                          {item.badge && <span className="bg-accent-blue/10 text-accent-blue border border-accent-blue/20 px-1.5 py-0.5 rounded text-[8px] font-black uppercase">{item.badge}</span>}
                        </div>
                        <p className="text-[10px] text-text-muted mt-1 leading-relaxed opacity-60 group-hover:opacity-100 transition-opacity">{item.desc}</p>
                      </div>
                      <button 
                        onClick={() => handleToggle(item.id)}
                        className={`w-10 h-5 rounded-full relative transition-all flex-shrink-0 ${toggles[item.id] ? 'bg-accent-red' : 'bg-bg-primary'}`}
                      >
                        <div className={`absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-all ${toggles[item.id] ? 'translate-x-5' : 'translate-x-0'}`} />
                      </button>
                    </div>
                  ))}
                </div>
              </section>

              <section>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-black text-text-primary uppercase tracking-[0.2em]">Detection Sensitivity</h3>
                  <span className="text-xl font-black text-accent-red tracking-tight">{sensitivity}%</span>
                </div>
                <div className="relative group">
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={sensitivity} 
                    onChange={(e) => setSensitivity(parseInt(e.target.value))}
                    className="w-full h-1.5 bg-bg-primary rounded-lg appearance-none cursor-pointer accent-accent-red"
                  />
                  <div className="flex justify-between mt-2 text-[9px] font-bold text-text-muted uppercase tracking-widest px-1">
                    <span>Performance</span>
                    <span>Accuracy</span>
                  </div>
                </div>
              </section>

              <section className="bg-bg-primary/50 border border-border-custom rounded-2xl p-6">
                <h4 className="text-[10px] font-black text-text-primary uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                  <ShieldCheck size={14} className="text-accent-blue" />
                  Zero Trust Privacy Protocol
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8">
                  {[
                    'End-to-end encrypted analysis',
                    'Zero local storage of voice data',
                    'Anonymized metadata indexing',
                    'Self-sovereign identity verification'
                  ].map((line, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <CheckCircle2 size={12} className="text-accent-green" />
                      <span className="text-[10px] font-medium text-text-muted italic opacity-80">{line}</span>
                    </div>
                  ))}
                </div>
              </section>

              <div className="pt-8 border-t border-border-custom flex items-center gap-4">
                <button 
                  onClick={handleSave}
                  disabled={saving}
                  className="bg-accent-red hover:bg-red-600 disabled:opacity-50 text-white px-8 py-3 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all shadow-lg shadow-accent-red/30 flex items-center gap-2"
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button 
                  className="bg-bg-primary border border-border-custom text-text-muted hover:text-text-primary px-8 py-3 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all flex items-center gap-2"
                >
                  <RotateCcw size={16} />
                  Reset Defaults
                </button>
              </div>
            </div>
          )}

          {activeTab !== 'vox' && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4">
              <div className="h-16 w-16 bg-bg-primary rounded-3xl flex items-center justify-center text-text-muted italic border-2 border-dashed border-border-custom">
                ...
              </div>
              <p className="text-xs font-bold text-text-muted uppercase tracking-widest italic opacity-60">This configuration panel is coming soon.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
