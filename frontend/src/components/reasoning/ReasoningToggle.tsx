/**
 * Reasoning Toggle Component
 * 
 * Toggle switch for enabling/disabling visible reasoning (Deep Thinking).
 * Includes visual feedback, accessibility, and optional labels.
 * 
 * AGENTS_FRONTEND.md compliant:
 * - WCAG 2.1 AA accessibility (keyboard navigation, screen readers)
 * - Smooth animations
 * - TypeScript strict mode
 * - Responsive design
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap } from 'lucide-react';
import type { ReasoningToggleProps } from '@/types/reasoning.types';

/**
 * Utility for merging class names
 */
const cn = (...classes: (string | boolean | undefined)[]) =>
  classes.filter(Boolean).join(' ');

/**
 * Reasoning Toggle Component
 * 
 * Allows users to enable/disable visible reasoning (Deep Thinking feature).
 * Shows current state with animated icons and smooth transitions.
 * 
 * @example
 * ```tsx
 * <ReasoningToggle
 *   enabled={reasoningEnabled}
 *   onChange={setReasoningEnabled}
 *   showLabel={true}
 * />
 * ```
 */
export const ReasoningToggle: React.FC<ReasoningToggleProps> = ({
  enabled,
  onChange,
  disabled = false,
  className,
  showLabel = true
}) => {
  const handleToggle = () => {
    if (!disabled) {
      onChange(!enabled);
    }
  };
  
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleToggle();
    }
  };
  
  return (
    <div
      className={cn(
        'reasoning-toggle inline-flex items-center gap-3',
        disabled && 'opacity-50 cursor-not-allowed',
        !disabled && 'cursor-pointer',
        className
      )}
      data-testid="reasoning-toggle"
    >
      {/* Label (optional) */}
      {showLabel && (
        <span
          className={cn(
            'text-sm font-medium',
            'text-gray-700 dark:text-gray-300',
            disabled && 'cursor-not-allowed'
          )}
          onClick={!disabled ? handleToggle : undefined}
        >
          Deep Thinking
        </span>
      )}
      
      {/* Toggle switch */}
      <button
        type="button"
        role="switch"
        aria-checked={enabled}
        aria-label={enabled ? 'Disable deep thinking mode' : 'Enable deep thinking mode'}
        disabled={disabled}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        className={cn(
          'relative inline-flex h-6 w-11 items-center rounded-full',
          'transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          'dark:focus:ring-offset-gray-900',
          enabled
            ? 'bg-blue-600 dark:bg-blue-500'
            : 'bg-gray-300 dark:bg-gray-600',
          disabled && 'cursor-not-allowed'
        )}
        data-testid="reasoning-toggle-switch"
      >
        {/* Toggle knob with icon */}
        <motion.span
          layout
          className={cn(
            'inline-flex items-center justify-center',
            'h-5 w-5 rounded-full',
            'bg-white shadow-sm',
            'transform transition-transform duration-200 ease-in-out'
          )}
          animate={{
            x: enabled ? 20 : 2
          }}
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 30
          }}
        >
          <motion.div
            initial={false}
            animate={{
              scale: enabled ? 1 : 0.8,
              rotate: enabled ? 0 : -180
            }}
            transition={{ duration: 0.2 }}
          >
            {enabled ? (
              <Brain className="w-3 h-3 text-blue-600" aria-hidden="true" />
            ) : (
              <Zap className="w-3 h-3 text-gray-400" aria-hidden="true" />
            )}
          </motion.div>
        </motion.span>
      </button>
      
      {/* Status indicator (optional) */}
      {showLabel && (
        <span
          className={cn(
            'text-xs font-medium',
            enabled
              ? 'text-blue-600 dark:text-blue-400'
              : 'text-gray-500 dark:text-gray-400'
          )}
        >
          {enabled ? 'On' : 'Off'}
        </span>
      )}
    </div>
  );
};

/**
 * Compact Reasoning Toggle
 * Minimal version without label for inline use
 */
export const CompactReasoningToggle: React.FC<{
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  disabled?: boolean;
  className?: string;
}> = ({ enabled, onChange, disabled = false, className }) => {
  return (
    <ReasoningToggle
      enabled={enabled}
      onChange={onChange}
      disabled={disabled}
      showLabel={false}
      className={className}
    />
  );
};

/**
 * Reasoning Toggle with Description
 * Extended version with help text
 */
export const ReasoningToggleWithDescription: React.FC<{
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  disabled?: boolean;
  className?: string;
}> = ({ enabled, onChange, disabled = false, className }) => {
  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-900 dark:text-gray-100">
            Deep Thinking Mode
          </label>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
            {enabled
              ? 'AI will show its step-by-step reasoning process'
              : 'AI will respond quickly without showing reasoning'}
          </p>
        </div>
        
        <ReasoningToggle
          enabled={enabled}
          onChange={onChange}
          disabled={disabled}
          showLabel={false}
        />
      </div>
      
      {/* Feature hints */}
      {enabled && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className={cn(
            'flex items-start gap-2 p-2 rounded-md',
            'bg-blue-50 dark:bg-blue-900/20',
            'border border-blue-200 dark:border-blue-800'
          )}
        >
          <Brain className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">Deep Thinking Active</p>
            <ul className="space-y-0.5 list-disc list-inside">
              <li>See AI's thought process</li>
              <li>Understand reasoning steps</li>
              <li>Learn problem-solving strategies</li>
            </ul>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ReasoningToggle;
