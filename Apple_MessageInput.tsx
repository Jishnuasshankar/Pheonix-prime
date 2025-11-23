import React, { useRef, useState, useCallback, useEffect, useLayoutEffect } from 'react';
import { Send, Smile, Paperclip, Loader2, X, Plus, Image as ImageIcon } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// ============================================================================
// 1. UTILITIES & DESIGN SYSTEM MOCKS
// ============================================================================

/**
 * Merges Tailwind classes with conflict resolution.
 */
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * High-performance Tooltip Component.
 * Supports the enhanced design without external dependencies.
 */
const Tooltip = ({ content, children, side = 'top' }: { content: string; children: React.ReactNode; side?: 'top' | 'bottom' }) => {
  const [show, setShow] = useState(false);
  
  return (
    <div 
      className="relative flex items-center justify-center group" 
      onMouseEnter={() => setShow(true)} 
      onMouseLeave={() => setShow(false)}
      onFocus={() => setShow(true)}
      onBlur={() => setShow(false)}
    >
      {children}
      <div className={cn(
        "absolute pointer-events-none px-3 py-1.5 text-[11px] font-semibold tracking-wide text-white/90 bg-[#1a1a1a]/90 backdrop-blur-xl rounded-full border border-white/10 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.5)] z-50 whitespace-nowrap transition-all duration-300 ease-[cubic-bezier(0.23,1,0.32,1)]",
        side === 'top' ? "bottom-full mb-2 origin-bottom" : "top-full mt-2 origin-top",
        show ? "opacity-100 scale-100 translate-y-0" : "opacity-0 scale-90 translate-y-1"
      )}>
        {content}
      </div>
    </div>
  );
};

// ============================================================================
// 2. TYPES & INTERFACES (STRICTLY ORIGINAL + STYLE)
// ============================================================================

export interface MessageInputProps {
  /** Callback when message is sent */
  onSend: (message: string) => void | Promise<void>;
  
  /** Is sending disabled */
  disabled?: boolean;
  
  /** Placeholder text */
  placeholder?: string;
  
  /** Maximum character length */
  maxLength?: number;
  
  /** Show character counter */
  showCounter?: boolean;
  
  /** Enable emoji picker */
  enableEmoji?: boolean;
  
  /** Enable file attachments */
  enableAttachments?: boolean;
  
  /** Additional CSS classes */
  className?: string;
}

// ============================================================================
// 3. CUSTOM HOOK: BUSINESS LOGIC
// ============================================================================

const useMessageInputLogic = ({
  onSend,
  disabled,
  maxLength
}: Pick<MessageInputProps, 'onSend' | 'disabled' | 'maxLength'>) => {
  const [value, setValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [showTools, setShowTools] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const charCount = value.length;
  const limit = maxLength || 15000; 
  const isOverLimit = charCount > limit;
  const isNearLimit = charCount > limit * 0.9;
  const hasContent = value.trim().length > 0;

  // Auto-resize logic
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${newHeight}px`;
  }, []);

  useLayoutEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleSend = useCallback(async () => {
    if (!value.trim() || isOverLimit || disabled || isSending) return;

    setIsSending(true);
    try {
      await onSend(value.trim());
      setValue('');
      requestAnimationFrame(() => {
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
          textareaRef.current.focus();
        }
      });
    } catch (err) {
      console.error('Send failed', err);
    } finally {
      setIsSending(false);
    }
  }, [value, isOverLimit, disabled, isSending, onSend]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  return {
    value,
    setValue,
    isSending,
    isFocused,
    setIsFocused,
    hasContent,
    isOverLimit,
    isNearLimit,
    charCount,
    limit, // Returned limit here to fix ReferenceError
    textareaRef,
    handleSend,
    handleKeyDown,
    showTools,
    setShowTools
  };
};

// ============================================================================
// 4. SUB-COMPONENTS
// ============================================================================

const ActionButton = ({ 
  icon: Icon, 
  onClick, 
  active = false, 
  disabled = false, 
  label,
  className 
}: { 
  icon: React.ElementType, 
  onClick?: () => void, 
  active?: boolean, 
  disabled?: boolean, 
  label: string,
  className?: string
}) => (
  <Tooltip content={label}>
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      className={cn(
        "relative flex items-center justify-center w-9 h-9 rounded-full transition-all duration-300 ease-out active:scale-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
        active ? "bg-white/20 text-white" : "text-neutral-400 hover:text-white hover:bg-white/10",
        disabled && "opacity-40 cursor-not-allowed",
        className
      )}
    >
      <Icon className="w-5 h-5 stroke-[1.5px]" />
    </button>
  </Tooltip>
);

const EmojiPicker = ({ onSelect, onClose }: { onSelect: (emoji: string) => void, onClose: () => void }) => (
  <div className="absolute bottom-full left-0 mb-4 z-50 origin-bottom-left animate-in slide-in-from-bottom-4 fade-in duration-300 ease-[cubic-bezier(0.23,1,0.32,1)]">
    <div className="bg-[#121212]/95 backdrop-blur-2xl border border-white/10 rounded-[32px] shadow-[0_8px_32px_-8px_rgba(0,0,0,0.6)] p-5 w-80">
      <div className="flex justify-between items-center mb-4 px-1">
        <span className="text-[13px] font-semibold text-white/40 tracking-widest uppercase">Quick Reactions</span>
        <button onClick={onClose} className="text-white/40 hover:text-white transition-colors p-1 bg-white/5 rounded-full hover:bg-white/10">
          <X className="w-3 h-3" />
        </button>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {['😊','😂','❤️','👍','🔥','🎉','😢','😮','👀','✨','🤝','💯','🙏','🚀'].map((emoji, i) => (
          <button
            key={emoji}
            onClick={() => onSelect(emoji)}
            style={{ animationDelay: `${i * 15}ms` }}
            className="w-8 h-8 flex items-center justify-center text-lg rounded-full hover:bg-white/10 transition-all hover:scale-125 active:scale-90 animate-in zoom-in-50 fade-in duration-300"
          >
            {emoji}
          </button>
        ))}
      </div>
      <div className="absolute -bottom-2 left-8 w-4 h-4 bg-[#121212]/95 border-r border-b border-white/10 transform rotate-45"></div>
    </div>
  </div>
);

// ============================================================================
// 5. MAIN COMPONENT
// ============================================================================

export const MessageInput: React.FC<MessageInputProps> = (props) => {
  const {
    value,
    setValue,
    isSending,
    isFocused,
    setIsFocused,
    hasContent,
    isOverLimit,
    isNearLimit,
    charCount,
    limit, // Destructured limit here
    textareaRef,
    handleSend,
    handleKeyDown,
    showTools,
    setShowTools
  } = useMessageInputLogic(props);

  const [showEmoji, setShowEmoji] = useState(false);
  const { 
    placeholder = "Type your message...", 
    enableAttachments = false, 
    enableEmoji = true, 
    showCounter = true,
    disabled = false 
  } = props;

  // Dynamic Styles based on state
  const containerClasses = cn(
    'relative flex items-end gap-2 p-1.5 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] border',
    'backdrop-blur-[20px]',
    isFocused 
      ? 'bg-[#1a1a1a]/80 border-white/15 shadow-[0_0_0_1px_rgba(255,255,255,0.05),0_10px_40px_-10px_rgba(0,0,0,0.5)] rounded-[28px]' 
      : 'bg-[#0a0a0a]/60 border-white/5 hover:border-white/10 rounded-[26px]',
    disabled && 'opacity-50 grayscale pointer-events-none'
  );

  return (
    <div className={cn('w-full font-sans antialiased group/container', props.className)}>
      
      {/* 1. Main Interaction Layer */}
      <div className={containerClasses}>
        
        {/* Left Accessory Stack */}
        <div className="flex items-center gap-1 pb-1.5 pl-1.5 transition-all duration-300 ease-out">
          {enableAttachments && (
            <>
              <div className={cn(
                "flex items-center gap-1 overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
                showTools ? "w-auto opacity-100 mr-1" : "w-0 opacity-0 mr-0"
              )}>
                <ActionButton 
                  label="Add Photo" 
                  icon={ImageIcon} 
                  className="bg-neutral-800/50 hover:bg-neutral-700/80"
                />
                <ActionButton 
                  label="Add File" 
                  icon={Paperclip} 
                  className="bg-neutral-800/50 hover:bg-neutral-700/80" 
                />
              </div>
              
              <button
                onClick={() => setShowTools(!showTools)}
                className={cn(
                  "flex items-center justify-center w-8 h-8 rounded-full transition-all duration-300 bg-neutral-800/80 text-neutral-400 hover:text-white hover:bg-neutral-700 active:scale-90",
                  showTools && "bg-neutral-700 text-white rotate-45"
                )}
              >
                <Plus className="w-5 h-5" />
              </button>
            </>
          )}
        </div>

        {/* Text Input Area */}
        <div className="flex-1 relative min-w-0 py-2.5 px-2">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled || isSending}
            rows={1}
            className={cn(
              'w-full bg-transparent text-white placeholder:text-neutral-500/80',
              'text-[15px] leading-[1.5] tracking-wide',
              'resize-none outline-none border-none ring-0',
              'min-h-[24px] max-h-[200px]',
              'scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent hover:scrollbar-thumb-white/20'
            )}
            style={{ 
              overflowY: textareaRef.current && textareaRef.current.scrollHeight > 200 ? 'auto' : 'hidden' 
            }}
          />
        </div>

        {/* Right Accessory Stack */}
        <div className="flex items-end gap-2 pb-1.5 pr-1.5">
          {enableEmoji && (
            <ActionButton 
              label="Emoji" 
              icon={Smile} 
              active={showEmoji}
              onClick={() => setShowEmoji(!showEmoji)}
            />
          )}

          {/* Send Button */}
          <Tooltip content={isOverLimit ? "Too long" : "Send"}>
            <button
              onClick={handleSend}
              disabled={isSending || isOverLimit || !hasContent}
              className={cn(
                "relative flex items-center justify-center w-9 h-9 rounded-full transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]",
                !hasContent && !isSending 
                   ? "bg-white/5 text-neutral-500 cursor-not-allowed opacity-50" 
                   : isOverLimit 
                   ? "bg-red-500/20 text-red-500" 
                   : "bg-white text-black hover:scale-110 shadow-[0_0_20px_-5px_rgba(255,255,255,0.4)] active:scale-90"
              )}
            >
              {isSending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className={cn("w-4 h-4 transition-all", hasContent ? "ml-0.5 fill-current" : "")} strokeWidth={2.5} />
              )}
            </button>
          </Tooltip>
        </div>
      </div>

      {/* 2. Feedback Layer (Counters) */}
      {showCounter && (
        <div className="absolute top-full right-4 mt-2 overflow-hidden pointer-events-none">
          <div className={cn(
            "px-3 py-1 rounded-full text-[10px] font-medium backdrop-blur-md transition-all duration-500",
            hasContent ? "translate-y-0 opacity-100" : "-translate-y-4 opacity-0",
            isOverLimit ? "bg-red-500/10 text-red-400 border border-red-500/20" : 
            isNearLimit ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : 
            "text-neutral-600"
          )}>
             {charCount.toLocaleString()} / {limit.toLocaleString()}
          </div>
        </div>
      )}

      {/* 3. Popover Layer (Emoji) */}
      {showEmoji && <EmojiPicker onSelect={(e) => { setValue(v => v + e); }} onClose={() => setShowEmoji(false)} />}
      
    </div>
  );
};

MessageInput.displayName = 'MessageInput';

// ============================================================================
// 6. PREVIEW ENVIRONMENT (STRICTLY MINIMAL)
// ============================================================================

const App = () => {
  const handleSend = async (message: string) => {
    // Simulate API call
    console.log("Sending:", message);
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  return (
    <div className="min-h-screen w-full bg-[#000000] text-neutral-200 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center opacity-40 text-xs uppercase tracking-[0.2em]">
          Black Variant • Component Preview
        </div>
        
        {/* Render Only the MessageInput as requested */}
        <MessageInput 
          onSend={handleSend}
          enableAttachments={true}
          enableEmoji={true}
          placeholder="Type a message..."
        />
      </div>
    </div>
  );
};

export default App;