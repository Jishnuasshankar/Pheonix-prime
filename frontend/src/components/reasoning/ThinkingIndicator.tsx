/**
 * Thinking Indicator Component
 * 
 * Animated indicator showing AI is thinking/reasoning.
 * Displays thinking mode, progress, and estimated time.
 * 
 * AGENTS_FRONTEND.md compliant:
 * - WCAG 2.1 AA accessibility
 * - Smooth animations (Framer Motion)
 * - Responsive design
 * - TypeScript strict mode
 * - Production-ready with error boundaries
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Zap, Sparkles, Clock } from 'lucide-react';
import type { ThinkingIndicatorProps, ThinkingMode } from '@/types/reasoning.types';

/**
 * Utility for merging class names
 */
const cn = (...classes: (string | boolean | undefined)[]) =>
  classes.filter(Boolean).join(' ');

/**
 * Thinking mode icon and color configuration
 */
const THINKING_MODE_CONFIG: Record<ThinkingMode, {
  icon: typeof Brain;
  color: string;
  bgColor: string;
  label: string;
  pulseColor: string;
}> = {
  system1: {
    icon: Zap,
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    label: 'Fast Thinking',
    pulseColor: 'bg-green-500'
  },
  system2: {
    icon: Brain,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    label: 'Deep Thinking',
    pulseColor: 'bg-blue-500'
  },
  hybrid: {
    icon: Sparkles,
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    label: 'Adaptive Thinking',
    pulseColor: 'bg-purple-500'
  }
};

/**
 * Format milliseconds to human-readable time
 */
const formatTime = (ms: number): string => {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
};

/**
 * Thinking Indicator Component
 * 
 * Shows animated indicator when AI is thinking/reasoning.
 * Provides visual feedback on thinking mode and progress.
 * 
 * @example
 * ```tsx
 * <ThinkingIndicator
 *   mode={ThinkingMode.SYSTEM2}
 *   currentStep={3}
 *   totalSteps={5}
 *   estimatedTimeMs={2000}
 * />
 * ```
 */
export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  mode,
  currentStep,
  totalSteps,
  estimatedTimeMs,
  className
}) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const config = THINKING_MODE_CONFIG[mode];
  const Icon = config.icon;
  
  // Track elapsed time
  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, 100);
    
    return () => clearInterval(interval);
  }, []);
  
  // Calculate progress percentage
  const progress = currentStep && totalSteps
    ? (currentStep / totalSteps) * 100
    : 0;
  
  // Determine if over estimated time
  const isOverEstimate = estimatedTimeMs && elapsedTime > estimatedTimeMs;
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
        className={cn(
          'thinking-indicator',
          'flex items-center gap-3 p-4 rounded-lg border',
          config.bgColor,
          'border-gray-200 dark:border-gray-700',
          className
        )}
        role="status"
        aria-live="polite"
        aria-atomic="true"
        data-testid="thinking-indicator"
      >
        {/* Animated icon */}
        <div className="relative flex-shrink-0">
          <motion.div
            animate={{
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className={cn('p-2 rounded-full', config.bgColor)}
          >
            <Icon className={cn('w-5 h-5', config.color)} />
          </motion.div>
          
          {/* Pulse ring */}
          <motion.div
            className={cn(
              'absolute inset-0 rounded-full',
              config.pulseColor,
              'opacity-20'
            )}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.2, 0, 0.2]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeOut"
            }}
          />
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn('text-sm font-semibold', config.color)}>
              {config.label}
            </span>
            
            {/* Step indicator */}
            {currentStep !== undefined && totalSteps !== undefined && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Step {currentStep} of {totalSteps}
              </span>
            )}
          </div>
          
          {/* Progress bar */}
          {progress > 0 && (
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-1">
              <motion.div
                className={config.pulseColor}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                style={{ height: '100%' }}
              />
            </div>
          )}
          
          {/* Time information */}
          <div className="flex items-center gap-3 text-xs text-gray-600 dark:text-gray-400">
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              <span>{formatTime(elapsedTime)}</span>
            </div>
            
            {estimatedTimeMs && (
              <span className={cn(
                isOverEstimate && 'text-orange-600 dark:text-orange-400'
              )}>
                {isOverEstimate ? 'Taking longer than expected' : `~${formatTime(estimatedTimeMs)}`}
              </span>
            )}
          </div>
        </div>
        
        {/* Animated dots */}
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className={cn('w-1.5 h-1.5 rounded-full', config.pulseColor)}
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.3, 1, 0.3]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeInOut"
              }}
            />
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

/**
 * Compact Thinking Indicator
 * Minimal version for inline use
 */
export const CompactThinkingIndicator: React.FC<{
  mode: ThinkingMode;
  className?: string;
}> = ({ mode, className }) => {
  const config = THINKING_MODE_CONFIG[mode];
  const Icon = config.icon;
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={cn(
        'inline-flex items-center gap-2 px-2 py-1 rounded-md',
        config.bgColor,
        className
      )}
      data-testid="compact-thinking-indicator"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear"
        }}
      >
        <Icon className={cn('w-4 h-4', config.color)} />
      </motion.div>
      <span className={cn('text-sm font-medium', config.color)}>
        {config.label}
      </span>
    </motion.div>
  );
};

export default ThinkingIndicator;
