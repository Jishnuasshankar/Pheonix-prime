import React, { useState, useCallback, useMemo, useRef } from 'react';

// Type Definitions
interface Assistant {
  id: string;
  name: string;
  role: string;
  description: string;
  letter: string;
  lastMessage: string;
  timestamp: string;
  isOnline: boolean;
  model: string;
  category: string;
  expertise: string[];
  gradientFrom: string;
  gradientTo: string;
  messageCount: number;
}

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isTyping?: boolean;
}

// Icon Components
const HomeIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
    <polyline points="9 22 9 12 15 12 15 22"/>
  </svg>
);

const MessageSquareIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
);

const SettingsIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const UserIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const SearchIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <path d="m21 21-4.35-4.35"/>
  </svg>
);

const PlusIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5v14m-7-7h14"/>
  </svg>
);

const ChevronLeftIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="15 18 9 12 15 6"/>
  </svg>
);

const ChevronRightIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="9 18 15 12 9 6"/>
  </svg>
);

const BrainIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
  </svg>
);

const NetworkIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="2"/>
    <path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-3.92 7.94"/>
    <path d="M12 2v4m0 12v4"/>
  </svg>
);

const BuildingIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
    <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>
  </svg>
);

const ArrowUpIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 19V5m-7 7 7-7 7 7"/>
  </svg>
);

const PaperclipIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
  </svg>
);

const ImageIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    <circle cx="9" cy="9" r="2"/>
    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
  </svg>
);

const MicIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
  </svg>
);

const EllipsisIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <circle cx="12" cy="12" r="1.5"/>
    <circle cx="19" cy="12" r="1.5"/>
    <circle cx="5" cy="12" r="1.5"/>
  </svg>
);

// Avatar Component
const Avatar: React.FC<{
  letter: string;
  gradientFrom: string;
  gradientTo: string;
  size?: 'sm' | 'md' | 'lg';
  isOnline?: boolean;
}> = ({ letter, gradientFrom, gradientTo, size = 'md', isOnline }) => {
  const sizeClasses = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-12 h-12 text-base',
    lg: 'w-16 h-16 text-lg'
  };

  return (
    <div className="relative flex-shrink-0">
      <div 
        className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-bold text-white shadow-xl`}
        style={{ 
          background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`,
          boxShadow: `0 8px 32px ${gradientFrom}40`
        }}
      >
        <span>{letter}</span>
      </div>
      {isOnline && (
        <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-[#0a0a0f] shadow-lg">
          <div className="w-full h-full bg-emerald-400 rounded-full animate-pulse opacity-75"></div>
        </div>
      )}
    </div>
  );
};

// Assistant Card
const AssistantCard: React.FC<{
  assistant: Assistant;
  isActive: boolean;
  onClick: () => void;
}> = ({ assistant, isActive, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`w-full px-4 py-3 flex items-start gap-3 rounded-2xl transition-all duration-300 ${
        isActive 
          ? 'bg-gradient-to-br from-blue-500/15 to-purple-500/15 shadow-lg' 
          : 'hover:bg-white/[0.04]'
      }`}
      style={{ backdropFilter: 'blur(20px)' }}
    >
      {isActive && (
        <div 
          className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-12 rounded-r-full"
          style={{
            background: `linear-gradient(to bottom, ${assistant.gradientFrom}, ${assistant.gradientTo})`,
            boxShadow: `0 0 20px ${assistant.gradientFrom}80`
          }}
        ></div>
      )}
      
      <Avatar 
        letter={assistant.letter}
        gradientFrom={assistant.gradientFrom}
        gradientTo={assistant.gradientTo}
        size="sm"
        isOnline={assistant.isOnline}
      />
      
      <div className="flex-1 min-w-0 text-left">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-bold text-white text-sm truncate">{assistant.name}</h3>
          {assistant.timestamp && (
            <span className="text-[10px] text-white/40 ml-2 flex-shrink-0 font-semibold">{assistant.timestamp.toUpperCase()}</span>
          )}
        </div>
        <div className="text-xs text-white/50 mb-1.5 font-medium truncate">{assistant.role}</div>
        <div className="flex items-center gap-2">
          <span 
            className="px-2 py-0.5 text-[10px] rounded-full font-bold backdrop-blur-xl border"
            style={{
              background: `linear-gradient(135deg, ${assistant.gradientFrom}30, ${assistant.gradientTo}30)`,
              borderColor: `${assistant.gradientFrom}40`,
              color: assistant.gradientFrom
            }}
          >
            {assistant.category}
          </span>
          {assistant.lastMessage && (
            <p className="text-[11px] text-white/40 truncate flex-1">{assistant.lastMessage}</p>
          )}
        </div>
      </div>
    </button>
  );
};

// Left Navigation Panel
const LeftNavigation: React.FC<{
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}> = ({ sidebarOpen, onToggleSidebar }) => {
  const [activeNav, setActiveNav] = useState('chats');

  const navItems = [
    { id: 'home', icon: HomeIcon, label: 'Home' },
    { id: 'chats', icon: MessageSquareIcon, label: 'Chats' },
    { id: 'settings', icon: SettingsIcon, label: 'Settings' },
    { id: 'profile', icon: UserIcon, label: 'Profile' }
  ];

  return (
    <div className="w-16 bg-[#0a0a0f] border-r border-white/[0.08] flex flex-col items-center py-6 gap-4">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => {
            setActiveNav(item.id);
            if (item.id === 'chats' && !sidebarOpen) {
              onToggleSidebar();
            }
          }}
          className={`p-3 rounded-xl transition-all duration-200 relative group ${
            activeNav === item.id
              ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20'
              : 'hover:bg-white/[0.05]'
          }`}
          title={item.label}
        >
          <item.icon className={`w-6 h-6 ${activeNav === item.id ? 'text-blue-400' : 'text-white/60'}`} />
          {activeNav === item.id && (
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-r-full"></div>
          )}
        </button>
      ))}
    </div>
  );
};

// Sidebar Component
const Sidebar: React.FC<{
  assistants: Assistant[];
  activeAssistantId: string;
  onAssistantSelect: (id: string) => void;
  isOpen: boolean;
}> = ({ assistants, activeAssistantId, onAssistantSelect, isOpen }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAssistants = useMemo(() => {
    return assistants.filter(assistant =>
      assistant.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [assistants, searchQuery]);

  if (!isOpen) return null;

  return (
    <aside className="w-80 flex flex-col h-screen border-r border-white/[0.08]" style={{ backdropFilter: 'blur(40px)', background: 'linear-gradient(to bottom, #0a0a0f, #13131a)' }}>
      <div className="p-6 border-b border-white/[0.08]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Avatar 
              letter="M" 
              gradientFrom="#0066FF"
              gradientTo="#6E3AFA"
              size="md"
            />
            <div>
              <h1 className="text-2xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">MasterX</h1>
              <p className="text-[10px] text-white/40 font-bold tracking-widest">AI EXCELLENCE</p>
            </div>
          </div>
          <button className="p-2.5 hover:bg-white/[0.08] rounded-xl transition-all duration-200">
            <PlusIcon className="w-4 h-4 text-white/60" />
          </button>
        </div>
        
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="search"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/30 text-white text-sm pl-10 pr-4 py-3 rounded-xl border border-white/[0.08] focus:border-blue-500/50 focus:outline-none placeholder:text-white/30 transition-all duration-200"
          />
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-3">
        <div className="space-y-2">
          {filteredAssistants.map((assistant) => (
            <AssistantCard
              key={assistant.id}
              assistant={assistant}
              isActive={activeAssistantId === assistant.id}
              onClick={() => onAssistantSelect(assistant.id)}
            />
          ))}
        </div>
      </nav>
    </aside>
  );
};

// Right Panel Component
const RightPanel: React.FC<{ isOpen: boolean }> = ({ isOpen }) => {
  if (!isOpen) return null;

  const tools = [
    {
      id: 'mindmap',
      name: 'Mind Map',
      icon: NetworkIcon,
      description: 'Visualize ideas and connections',
      gradientFrom: '#4E65FF',
      gradientTo: '#92EFFD'
    },
    {
      id: 'mindpalace',
      name: 'Mind Palace',
      icon: BuildingIcon,
      description: 'Memory organization system',
      gradientFrom: '#F093FB',
      gradientTo: '#F5576C'
    }
  ];

  return (
    <aside className="w-96 border-l border-white/[0.08] flex flex-col h-screen" style={{ backdropFilter: 'blur(40px)', background: 'linear-gradient(to bottom, #0a0a0f, #13131a)' }}>
      <div className="p-6 border-b border-white/[0.08]">
        <h2 className="text-xl font-bold text-white mb-2">Tools & Components</h2>
        <p className="text-sm text-white/50">Enhance your workflow with AI-powered tools</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 gap-4">
          {tools.map((tool) => (
            <button
              key={tool.id}
              className="p-6 rounded-2xl border border-white/[0.08] hover:border-white/[0.15] transition-all duration-300 text-left group hover:scale-[1.02]"
              style={{
                background: `linear-gradient(135deg, ${tool.gradientFrom}10, ${tool.gradientTo}10)`,
                backdropFilter: 'blur(20px)'
              }}
            >
              <div 
                className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-xl"
                style={{
                  background: `linear-gradient(135deg, ${tool.gradientFrom}, ${tool.gradientTo})`,
                  boxShadow: `0 8px 32px ${tool.gradientFrom}40`
                }}
              >
                <tool.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{tool.name}</h3>
              <p className="text-sm text-white/60">{tool.description}</p>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};

// Chat Header
const ChatHeader: React.FC<{ 
  assistant: Assistant;
  onToggleRightPanel: () => void;
}> = ({ assistant, onToggleRightPanel }) => {
  return (
    <header className="h-20 border-b border-white/[0.08] flex items-center justify-between px-8 backdrop-blur-2xl">
      <div className="flex items-center gap-4">
        <Avatar 
          letter={assistant.letter}
          gradientFrom={assistant.gradientFrom}
          gradientTo={assistant.gradientTo}
          size="md"
          isOnline={assistant.isOnline}
        />
        <div>
          <h2 className="font-bold text-white text-lg">{assistant.name}</h2>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 text-white/50">
              <BrainIcon className="w-3.5 h-3.5" />
              <span className="font-semibold">{assistant.model}</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="font-semibold">Active</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <button 
          onClick={onToggleRightPanel}
          className="p-2.5 hover:bg-white/[0.08] rounded-xl transition-all duration-200"
        >
          <ChevronLeftIcon className="w-5 h-5 text-white/60" />
        </button>
        <button className="p-2.5 hover:bg-white/[0.08] rounded-xl transition-all duration-200">
          <EllipsisIcon className="w-5 h-5 text-white/60" />
        </button>
      </div>
    </header>
  );
};

// Empty State
const EmptyState: React.FC<{ assistant: Assistant }> = ({ assistant }) => {
  return (
    <div className="flex-1 flex items-center justify-center px-8">
      <div className="text-center max-w-2xl">
        <div className="mb-8 text-8xl">👋</div>
        <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Hello, I'm {assistant.name}
        </h2>
        <p className="text-white/60 text-lg mb-6">{assistant.description}</p>
        <div className="flex items-center justify-center gap-3">
          <span className="px-4 py-2 rounded-full bg-white/[0.05] border border-white/[0.1] text-xs text-white/50 font-bold">
            {assistant.model}
          </span>
          <span className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 text-xs text-blue-400 font-bold">
            ULTRA MODE
          </span>
        </div>
      </div>
    </div>
  );
};

// Message Input - CENTERED
const MessageInput: React.FC<{
  onSendMessage: (content: string) => void;
  assistant: Assistant;
}> = ({ onSendMessage, assistant }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(() => {
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [message, onSendMessage]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  }, []);

  return (
    <div className="border-t border-white/[0.08] backdrop-blur-2xl p-8">
      <div className="max-w-4xl mx-auto">
        <div 
          className="rounded-3xl border-2 transition-all duration-300"
          style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04))',
            backdropFilter: 'blur(40px)',
            borderColor: 'rgba(255,255,255,0.1)'
          }}
        >
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={`Message ${assistant.name}...`}
            className="w-full bg-transparent text-white text-base px-6 py-4 resize-none focus:outline-none placeholder:text-white/30 font-medium leading-relaxed"
            rows={1}
            style={{ maxHeight: '200px', minHeight: '56px' }}
          />
          
          <div className="flex items-center justify-between px-4 py-3 border-t border-white/[0.08]">
            <div className="flex items-center gap-1">
              <button className="p-2 hover:bg-white/[0.08] rounded-xl transition-all duration-200">
                <PaperclipIcon className="w-4 h-4 text-white/50" />
              </button>
              <button className="p-2 hover:bg-white/[0.08] rounded-xl transition-all duration-200">
                <ImageIcon className="w-4 h-4 text-white/50" />
              </button>
              <button className="p-2 hover:bg-white/[0.08] rounded-xl transition-all duration-200">
                <MicIcon className="w-4 h-4 text-white/50" />
              </button>
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={!message.trim()}
              className="px-5 py-2.5 rounded-xl flex items-center gap-2 transition-all duration-200 font-bold text-sm"
              style={{
                background: message.trim()
                  ? `linear-gradient(135deg, ${assistant.gradientFrom}, ${assistant.gradientTo})`
                  : 'rgba(100,100,100,0.3)',
                boxShadow: message.trim() ? `0 8px 24px ${assistant.gradientFrom}40` : 'none',
                cursor: message.trim() ? 'pointer' : 'not-allowed'
              }}
            >
              <span className="text-white">Send</span>
              <ArrowUpIcon className="w-4 h-4 text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App
const MasterX: React.FC = () => {
  const assistants: Assistant[] = useMemo(() => [
    {
      id: '1',
      name: 'Creative Director',
      role: 'Design & Innovation Specialist',
      description: 'Transform your creative vision into reality with cutting-edge design thinking.',
      letter: 'C',
      lastMessage: 'Let\'s create something extraordinary...',
      timestamp: 'now',
      isOnline: true,
      model: 'GPT-4 Turbo',
      category: 'Creative',
      expertise: ['UI/UX Design', 'Branding', 'Art Direction'],
      gradientFrom: '#FF6B6B',
      gradientTo: '#FF8E53',
      messageCount: 247
    },
    {
      id: '2',
      name: 'Code Architect',
      role: 'Senior Development Expert',
      description: 'Build robust, scalable applications with best practices.',
      letter: 'A',
      lastMessage: 'Building elegant solutions...',
      timestamp: '2m',
      isOnline: true,
      model: 'GPT-4 Advanced',
      category: 'Engineering',
      expertise: ['Full-Stack', 'System Design'],
      gradientFrom: '#4E65FF',
      gradientTo: '#92EFFD',
      messageCount: 892
    },
    {
      id: '3',
      name: 'Data Scientist',
      role: 'Analytics & Machine Learning',
      description: 'Unlock insights from your data using advanced analytics.',
      letter: 'D',
      lastMessage: 'Analyzing patterns...',
      timestamp: '5m',
      isOnline: true,
      model: 'GPT-4 Analytics',
      category: 'Data Science',
      expertise: ['ML/AI', 'Statistics'],
      gradientFrom: '#00F5A0',
      gradientTo: '#00D9F5',
      messageCount: 564
    },
    {
      id: '4',
      name: 'Business Strategist',
      role: 'Growth & Strategy Consultant',
      description: 'Scale your business with data-driven strategies.',
      letter: 'B',
      lastMessage: 'Scaling your vision...',
      timestamp: '12m',
      isOnline: true,
      model: 'GPT-4 Business',
      category: 'Strategy',
      expertise: ['Strategy', 'Market Analysis'],
      gradientFrom: '#FEC163',
      gradientTo: '#DE4313',
      messageCount: 423
    },
    {
      id: '5',
      name: 'Content Creator',
      role: 'Writing & Storytelling',
      description: 'Craft compelling content that resonates with your audience.',
      letter: 'W',
      lastMessage: 'Crafting narratives...',
      timestamp: '25m',
      isOnline: true,
      model: 'GPT-4 Creative',
      category: 'Content',
      expertise: ['Copywriting', 'Storytelling'],
      gradientFrom: '#F093FB',
      gradientTo: '#F5576C',
      messageCount: 678
    },
    {
      id: '6',
      name: 'Marketing Guru',
      role: 'Brand & Campaign Strategy',
      description: 'Amplify your message with cutting-edge marketing strategies.',
      letter: 'M',
      lastMessage: 'Amplifying your message...',
      timestamp: '2h',
      isOnline: true,
      model: 'GPT-4 Marketing',
      category: 'Marketing',
      expertise: ['Digital Marketing', 'Campaign Management'],
      gradientFrom: '#FA709A',
      gradientTo: '#FEE140',
      messageCount: 512
    }
  ], []);

  const [activeAssistantId, setActiveAssistantId] = useState<string>('1');
  const [messages, setMessages] = useState<Message[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);

  const activeAssistant = useMemo(() => 
    assistants.find(a => a.id === activeAssistantId) || assistants[0],
    [assistants, activeAssistantId]
  );

  const handleSendMessage = useCallback((content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);

    setTimeout(() => {
      const response: Message = {
        id: (Date.now() + 1).toString(),
        content: `This is a response from ${activeAssistant.name}. In production, this would be powered by ${activeAssistant.model}.`,
        role: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, response]);
    }, 1000);
  }, [activeAssistant]);

  const handleAssistantSelect = useCallback((id: string) => {
    setActiveAssistantId(id);
    setMessages([]);
  }, []);

  return (
    <div className="flex h-screen text-white overflow-hidden" style={{ background: 'linear-gradient(to bottom, #0a0a0f, #0d0d15)' }}>
      {/* Left Navigation */}
      <LeftNavigation 
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Sidebar with Chat History */}
      <Sidebar
        assistants={assistants}
        activeAssistantId={activeAssistantId}
        onAssistantSelect={handleAssistantSelect}
        isOpen={sidebarOpen}
      />

      {/* Toggle Sidebar Button (when closed) */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="absolute left-16 top-6 z-50 p-2 bg-white/[0.08] hover:bg-white/[0.12] rounded-xl transition-all duration-200 backdrop-blur-xl border border-white/[0.08]"
        >
          <ChevronRightIcon className="w-5 h-5 text-white/60" />
        </button>
      )}

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        <ChatHeader 
          assistant={activeAssistant}
          onToggleRightPanel={() => setRightPanelOpen(!rightPanelOpen)}
        />
        
        {messages.length === 0 ? (
          <EmptyState assistant={activeAssistant} />
        ) : (
          <div className="flex-1 overflow-y-auto px-8 py-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <Avatar 
                      letter={activeAssistant.letter}
                      gradientFrom={activeAssistant.gradientFrom}
                      gradientTo={activeAssistant.gradientTo}
                      size="sm"
                    />
                  )}
                  <div className="max-w-2xl">
                    <div 
                      className="px-6 py-4 rounded-3xl backdrop-blur-xl border"
                      style={{
                        background: msg.role === 'user'
                          ? `linear-gradient(135deg, ${activeAssistant.gradientFrom}20, ${activeAssistant.gradientTo}20)`
                          : 'rgba(255,255,255,0.05)',
                        borderColor: msg.role === 'user' ? `${activeAssistant.gradientFrom}40` : 'rgba(255,255,255,0.1)'
                      }}
                    >
                      <p className="text-white/90 text-sm leading-relaxed">{msg.content}</p>
                    </div>
                    <div className={`mt-2 text-xs text-white/30 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                  {msg.role === 'user' && (
                    <Avatar 
                      letter="Y"
                      gradientFrom="#10B981"
                      gradientTo="#34D399"
                      size="sm"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Centered Message Input */}
        <MessageInput onSendMessage={handleSendMessage} assistant={activeAssistant} />
      </main>

      {/* Right Panel - Tools */}
      <RightPanel isOpen={rightPanelOpen} />

      {/* Toggle Right Panel Button (when closed) */}
      {!rightPanelOpen && (
        <button
          onClick={() => setRightPanelOpen(true)}
          className="absolute right-6 top-6 z-50 p-2 bg-white/[0.08] hover:bg-white/[0.12] rounded-xl transition-all duration-200 backdrop-blur-xl border border-white/[0.08]"
        >
          <ChevronLeftIcon className="w-5 h-5 text-white/60" />
        </button>
      )}
    </div>
  );
};

export default MasterX;