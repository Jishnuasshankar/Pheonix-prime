/**
 * MainApp Component - Core Application Container with Modern UI (Updated Design)
 * 
 * WCAG 2.1 AA Compliant:
 * - Semantic HTML structure
 * - Keyboard navigation (Ctrl+D dashboard, Ctrl+S settings, Ctrl+P profile, Ctrl+A analytics)
 * - Focus management for modals
 * - ARIA labels and roles
 * 
 * Performance:
 * - Code splitting for modals (lazy load)
 * - Virtualized message list
 * - Debounced emotion updates
 * - Optimized re-renders with React.memo
 * 
 * Backend Integration:
 * - Real-time chat with emotion detection
 * - WebSocket for live updates
 * - Analytics tracking
 * - Cost monitoring
 * - POST /api/v1/chat - Chat messaging
 * - WebSocket /api/ws - Real-time updates
 * 
 * NEW DESIGN FEATURES:
 * - Enhanced glassmorphism effects
 * - Better gradient styling
 * - Improved card designs
 * - Modern message input (centered)
 * - Better empty state
 * - Smooth animations and transitions
 */

import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { Helmet } from 'react-helmet-async';
import { useNavigate } from 'react-router-dom';
import {
  Home, MessageSquare, BarChart3, Trophy, Settings as SettingsIcon,
  User, Search, Plus, ChevronLeft, ChevronRight, Brain,
  Network, Building2, Wifi, WifiOff
} from 'lucide-react';

// Components
import { ChatContainer } from '@/components/chat/ChatContainer';
import { EmotionWidget } from '@/components/emotion/EmotionWidget';
import { AchievementNotificationManager } from '@/components/gamification/AchievementNotificationManager';
import { Skeleton } from '@/components/ui/Skeleton';

// Hooks
import { useAuth } from '@/hooks/useAuth';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAnalytics } from '@/hooks/useAnalytics';
import { useHotkeys } from '@/hooks/useHotkeys';
import { cn } from '@/utils/cn';

// Lazy load modals for better performance
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Settings = lazy(() => import('@/pages/Settings'));
const Profile = lazy(() => import('@/pages/Profile'));
const Analytics = lazy(() => import('@/pages/Analytics'));
const Achievements = lazy(() => import('@/pages/Achievements'));

// ============================================================================
// TYPES
// ============================================================================

export interface MainAppProps {
  /**
   * Initial view to show
   * @default "chat"
   */
  initialView?: 'chat' | 'dashboard' | 'settings' | 'profile';
}

type ModalType = 'dashboard' | 'settings' | 'profile' | 'analytics' | 'achievements' | null;

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  action: () => void;
}

// ============================================================================
// AVATAR COMPONENT - Enhanced with better styling
// ============================================================================

const Avatar: React.FC<{
  letter: string;
  gradientFrom: string;
  gradientTo: string;
  size?: 'sm' | 'md' | 'lg';
  isOnline?: boolean;
}> = React.memo(({ letter, gradientFrom, gradientTo, size = 'md', isOnline }) => {
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
});

Avatar.displayName = 'Avatar';

// ============================================================================
// LEFT NAVIGATION PANEL (Icon Sidebar) - Updated with all navigation items
// ============================================================================

const LeftNavigation: React.FC<{
  activeNav: string;
  onNavChange: (id: string) => void;
  onToggleChatSidebar: () => void;
  chatSidebarOpen: boolean;
}> = React.memo(({ activeNav, onNavChange, onToggleChatSidebar, chatSidebarOpen }) => {
  
  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, action: () => onNavChange('dashboard') },
    { id: 'chats', label: 'Chats', icon: MessageSquare, action: () => {
      onNavChange('chats');
      if (!chatSidebarOpen) onToggleChatSidebar();
    }},
    { id: 'analytics', label: 'Analytics', icon: BarChart3, action: () => onNavChange('analytics') },
    { id: 'achievements', label: 'Achievements', icon: Trophy, action: () => onNavChange('achievements') },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, action: () => onNavChange('settings') },
    { id: 'profile', label: 'Profile', icon: User, action: () => onNavChange('profile') }
  ];

  return (
    <div className="w-16 bg-[#0a0a0f] border-r border-white/[0.08] flex flex-col items-center py-6 gap-4">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={item.action}
          className={`p-3 rounded-xl transition-all duration-200 relative group ${
            activeNav === item.id
              ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20'
              : 'hover:bg-white/[0.05]'
          }`}
          title={item.label}
          aria-label={item.label}
        >
          <item.icon className={`w-6 h-6 ${activeNav === item.id ? 'text-blue-400' : 'text-white/60'}`} />
          {activeNav === item.id && (
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-r-full"></div>
          )}
        </button>
      ))}
    </div>
  );
});

LeftNavigation.displayName = 'LeftNavigation';

// ============================================================================
// CHAT SESSIONS SIDEBAR (Middle Column) - Enhanced design
// ============================================================================

const ChatSessionsSidebar: React.FC<{
  isOpen: boolean;
  user: any;
}> = React.memo(({ isOpen, user }) => {
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  return (
    <aside 
      className="w-80 flex flex-col h-screen border-r border-white/[0.08]" 
      style={{ 
        backdropFilter: 'blur(40px)', 
        background: 'linear-gradient(to bottom, #0a0a0f, #13131a)' 
      }}
    >
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
              <h1 className="text-2xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                MasterX
              </h1>
              <p className="text-[10px] text-white/40 font-bold tracking-widest">AI LEARNING</p>
            </div>
          </div>
          <button 
            className="p-2.5 hover:bg-white/[0.08] rounded-xl transition-all duration-200" 
            aria-label="New chat"
          >
            <Plus className="w-4 h-4 text-white/60" />
          </button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="search"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-black/30 text-white text-sm pl-10 pr-4 py-3 rounded-xl border border-white/[0.08] focus:border-blue-500/50 focus:outline-none placeholder:text-white/30 transition-all duration-200"
            aria-label="Search chats"
          />
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-3">
        <div className="space-y-2">
          {/* Active Chat Session - Enhanced card design */}
          <button
            className="w-full px-4 py-3 flex items-start gap-3 rounded-2xl transition-all duration-300 bg-gradient-to-br from-blue-500/15 to-purple-500/15 shadow-lg relative"
            style={{ backdropFilter: 'blur(20px)' }}
          >
            <div 
              className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-12 rounded-r-full bg-gradient-to-b from-blue-500 to-purple-500"
              style={{
                boxShadow: '0 0 20px rgba(59, 130, 246, 0.5)'
              }}
            ></div>
            
            <Avatar 
              letter={user?.name?.[0]?.toUpperCase() || 'U'}
              gradientFrom="#4E65FF"
              gradientTo="#92EFFD"
              size="sm"
              isOnline={true}
            />
            
            <div className="flex-1 min-w-0 text-left">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-bold text-white text-sm truncate">Current Session</h3>
                <span className="text-[10px] text-white/40 ml-2 flex-shrink-0 font-semibold">NOW</span>
              </div>
              <div className="text-xs text-white/50 mb-1.5 font-medium truncate">Learning Session</div>
              <div className="flex items-center gap-2">
                <span 
                  className="px-2 py-0.5 text-[10px] rounded-full font-bold backdrop-blur-xl border"
                  style={{
                    background: 'linear-gradient(135deg, rgba(78, 101, 255, 0.3), rgba(146, 239, 253, 0.3))',
                    borderColor: 'rgba(78, 101, 255, 0.4)',
                    color: '#4E65FF'
                  }}
                >
                  Active
                </span>
                <p className="text-[11px] text-white/40 truncate flex-1">Continue learning...</p>
              </div>
            </div>
          </button>
        </div>
      </nav>
    </aside>
  );
});

ChatSessionsSidebar.displayName = 'ChatSessionsSidebar';

// ============================================================================
// TOOLS PANEL (Right Column) - Enhanced with better styling
// ============================================================================

const ToolsPanel: React.FC<{ 
  isOpen: boolean;
  showEmotion: boolean;
}> = React.memo(({ isOpen, showEmotion }) => {
  if (!isOpen) return null;

  const tools = [
    {
      id: 'mindmap',
      name: 'Mind Map',
      icon: Network,
      description: 'Visualize ideas and connections',
      gradientFrom: '#4E65FF',
      gradientTo: '#92EFFD'
    },
    {
      id: 'mindpalace',
      name: 'Mind Palace',
      icon: Building2,
      description: 'Memory organization system',
      gradientFrom: '#F093FB',
      gradientTo: '#F5576C'
    }
  ];

  return (
    <aside 
      className="w-80 border-l border-white/[0.08] flex flex-col h-screen" 
      style={{ 
        backdropFilter: 'blur(40px)', 
        background: 'linear-gradient(to bottom, #0a0a0f, #13131a)' 
      }}
    >
      {/* Emotion Widget Section */}
      {showEmotion && (
        <div className="p-6 border-b border-white/[0.08]">
          <h2 className="text-lg font-bold text-white mb-4">Emotion Analysis</h2>
          <EmotionWidget
            size="expanded"
            showPAD={true}
            showReadiness={true}
            animate={true}
          />
        </div>
      )}

      {/* Tools Section */}
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
});

ToolsPanel.displayName = 'ToolsPanel';

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const MainApp: React.FC<MainAppProps> = ({
  initialView = 'chat'
}) => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { isConnected, subscribe } = useWebSocket();
  const { trackEvent, trackPageView } = useAnalytics();

  // Navigation state
  const [activeNav, setActiveNav] = useState<string>(initialView !== 'chat' ? initialView : 'chats');
  
  // Modal state
  const [activeModal, setActiveModal] = useState<ModalType>(
    initialView !== 'chat' ? initialView : null
  );

  // Sidebar states
  const [chatSidebarOpen, setChatSidebarOpen] = useState(true);
  const [toolsPanelOpen, setToolsPanelOpen] = useState(true);

  // -------------------------------------------------------------------------
  // Effects
  // -------------------------------------------------------------------------

  useEffect(() => {
    trackPageView('main_app');
    trackEvent('app_session_start');

    return () => {
      trackEvent('app_session_end');
    };
  }, [trackEvent, trackPageView]);

  // WebSocket subscriptions - Preserve all backend integrations
  useEffect(() => {
    if (!isConnected) return;

    // Subscribe to emotion updates
    const unsubEmotion = subscribe('emotion_update', (data: any) => {
      console.log('Emotion update:', data);
    });

    // Subscribe to notifications  
    const unsubNotifications = subscribe('notification', (data: any) => {
      console.log('Notification:', data);
      // Can be used for toast notifications in future
    });

    return () => {
      unsubEmotion();
      unsubNotifications();
    };
  }, [isConnected, subscribe]);

  // -------------------------------------------------------------------------
  // Navigation & Modal Handlers - Preserve all functionality
  // -------------------------------------------------------------------------

  const handleNavChange = useCallback((navId: string) => {
    setActiveNav(navId);
    
    // Open corresponding modal for non-chat items
    if (navId === 'dashboard') {
      handleOpenModal('dashboard');
    } else if (navId === 'analytics') {
      handleOpenModal('analytics');
    } else if (navId === 'achievements') {
      handleOpenModal('achievements');
    } else if (navId === 'settings') {
      handleOpenModal('settings');
    } else if (navId === 'profile') {
      handleOpenModal('profile');
    } else if (navId === 'chats') {
      handleCloseModal();
    }
  }, []);

  const handleOpenModal = useCallback((modal: ModalType) => {
    if (modal) {
      trackEvent('modal_open', { modal });
      setActiveModal(modal);
    }
  }, [trackEvent]);

  const handleCloseModal = useCallback(() => {
    if (activeModal) {
      trackEvent('modal_close', { modal: activeModal });
      setActiveModal(null);
      setActiveNav('chats');
    }
  }, [activeModal, trackEvent]);

  // -------------------------------------------------------------------------
  // Keyboard Shortcuts - Preserve all hotkeys
  // -------------------------------------------------------------------------

  useHotkeys('ctrl+d', (e) => {
    e.preventDefault();
    handleNavChange('dashboard');
  }, 'Open Dashboard');

  useHotkeys('ctrl+s', (e) => {
    e.preventDefault();
    handleNavChange('settings');
  }, 'Open Settings');

  useHotkeys('ctrl+p', (e) => {
    e.preventDefault();
    handleNavChange('profile');
  }, 'Open Profile');

  useHotkeys('ctrl+a', (e) => {
    e.preventDefault();
    handleNavChange('analytics');
  }, 'Open Analytics');

  useHotkeys('esc', () => {
    handleCloseModal();
  }, 'Close Modal');

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  if (!user) {
    // Redirect to login if not authenticated
    navigate('/login');
    return null;
  }

  return (
    <>
      {/* SEO */}
      <Helmet>
        <title>MasterX - AI Learning Platform</title>
        <meta name="description" content="Learn with emotion-aware AI" />
        <meta name="robots" content="noindex, nofollow" />
      </Helmet>

      <div 
        className="flex h-screen text-white overflow-hidden" 
        style={{ background: 'linear-gradient(to bottom, #0a0a0f, #0d0d15)' }}
      >
        {/* Left Navigation (Icon Sidebar) */}
        <LeftNavigation 
          activeNav={activeNav}
          onNavChange={handleNavChange}
          onToggleChatSidebar={() => setChatSidebarOpen(!chatSidebarOpen)}
          chatSidebarOpen={chatSidebarOpen}
        />

        {/* Chat Sessions Sidebar */}
        <ChatSessionsSidebar
          isOpen={chatSidebarOpen}
          user={user}
        />

        {/* Toggle Chat Sidebar Button (when closed) */}
        {!chatSidebarOpen && (
          <button
            onClick={() => setChatSidebarOpen(true)}
            className="absolute left-16 top-6 z-50 p-2 bg-white/[0.08] hover:bg-white/[0.12] rounded-xl transition-all duration-200 backdrop-blur-xl border border-white/[0.08]"
            aria-label="Open chat sidebar"
          >
            <ChevronRight className="w-5 h-5 text-white/60" />
          </button>
        )}

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-w-0 relative">
          {/* Chat Header - Enhanced styling */}
          <header className="h-20 border-b border-white/[0.08] flex items-center justify-between px-8 backdrop-blur-2xl">
            <div className="flex items-center gap-4">
              <Avatar 
                letter={user?.name?.[0]?.toUpperCase() || 'U'}
                gradientFrom="#0066FF"
                gradientTo="#6E3AFA"
                size="md"
                isOnline={true}
              />
              <div>
                <h2 className="font-bold text-white text-lg">Learning Session</h2>
                <div className="flex items-center gap-3 text-xs">
                  <div className="flex items-center gap-1.5 text-white/50">
                    <Brain className="w-3.5 h-3.5" />
                    <span className="font-semibold">AI Assistant</span>
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
                onClick={() => setToolsPanelOpen(!toolsPanelOpen)}
                className="p-2.5 hover:bg-white/[0.08] rounded-xl transition-all duration-200"
                aria-label="Toggle tools panel"
              >
                <ChevronLeft className="w-5 h-5 text-white/60" />
              </button>
            </div>
          </header>

          {/* Chat Container - Preserve original component and all functionality */}
          <div className="flex-1 overflow-hidden" data-testid="chat-container">
            <ChatContainer />
          </div>

          {/* WebSocket Status Indicator (Dev mode) - Preserve functionality */}
          {typeof window !== 'undefined' && window.location.hostname === 'localhost' && (
            <div className="absolute bottom-4 left-4 z-50">
              <div className={cn(
                "px-3 py-1 rounded-full text-xs font-medium flex items-center gap-2",
                isConnected 
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-red-500/20 text-red-400 border border-red-500/30"
              )}>
                {isConnected ? (
                  <>
                    <Wifi className="w-3 h-3" />
                    <span>Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-3 h-3" />
                    <span>Disconnected</span>
                  </>
                )}
              </div>
            </div>
          )}
        </main>

        {/* Right Panel - Tools & Emotion - Preserve EmotionWidget integration */}
        <ToolsPanel isOpen={toolsPanelOpen} showEmotion={true} />

        {/* Toggle Right Panel Button (when closed) */}
        {!toolsPanelOpen && (
          <button
            onClick={() => setToolsPanelOpen(true)}
            className="absolute right-6 top-6 z-50 p-2 bg-white/[0.08] hover:bg-white/[0.12] rounded-xl transition-all duration-200 backdrop-blur-xl border border-white/[0.08]"
            aria-label="Open tools panel"
          >
            <ChevronLeft className="w-5 h-5 text-white/60" />
          </button>
        )}

        {/* Modals (Lazy Loaded) - Preserve all modal functionality */}
        <Suspense fallback={<ModalSkeleton />}>
          {activeModal === 'dashboard' && (
            <Dashboard onClose={handleCloseModal} />
          )}
          {activeModal === 'settings' && (
            <Settings onClose={handleCloseModal} />
          )}
          {activeModal === 'profile' && (
            <Profile onClose={handleCloseModal} />
          )}
          {activeModal === 'analytics' && (
            <Analytics onClose={handleCloseModal} />
          )}
          {activeModal === 'achievements' && (
            <Achievements onClose={handleCloseModal} />
          )}
        </Suspense>

        {/* Global Achievement Notifications - Preserve integration */}
        <AchievementNotificationManager />
      </div>
    </>
  );
};

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

/**
 * Modal loading skeleton
 */
const ModalSkeleton: React.FC = () => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div className="w-full max-w-4xl h-[80vh] bg-[#13131a] rounded-2xl p-8 border border-white/[0.08]">
      <Skeleton className="h-8 w-64 mb-6" />
      <Skeleton className="h-48 w-full mb-4" />
      <Skeleton className="h-48 w-full mb-4" />
      <Skeleton className="h-32 w-full" />
    </div>
  </div>
);

// ============================================================================
// EXPORTS
// ============================================================================

export default MainApp;
