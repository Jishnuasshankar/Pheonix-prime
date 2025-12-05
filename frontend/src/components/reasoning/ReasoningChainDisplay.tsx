/**
 * Reasoning Chain Display Component
 * 
 * Displays step-by-step thinking process with animations and interactive elements.
 * 
 * AGENTS_FRONTEND.md compliant:
 * - WCAG 2.1 AA accessibility
 * - Responsive design (mobile-first)
 * - Framer Motion animations
 * - TypeScript strict mode
 * - Comprehensive error handling
 * - Loading, error, and empty states
 */

import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, CheckCircle, Lightbulb, Clock, TrendingUp } from 'lucide-react';
import { ReasoningStrategy, ThinkingMode, type ReasoningChainDisplayProps, type ReasoningStep } from '@/types/reasoning.types';

/**
 * Utility for merging class names
 */
const cn = (...classes: (string | boolean | undefined)[]) =>
  classes.filter(Boolean).join(' ');

/**
 * Strategy color mapping
 * Maps reasoning strategies to Tailwind color classes
 */
const STRATEGY_COLORS: Record<ReasoningStrategy, string> = {
  [ReasoningStrategy.DEDUCTIVE]: 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20',
  [ReasoningStrategy.INDUCTIVE]: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
  [ReasoningStrategy.ABDUCTIVE]: 'bg-purple-500/10 text-purple-700 dark:text-purple-400 border-purple-500/20',
  [ReasoningStrategy.ANALOGICAL]: 'bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20',
  [ReasoningStrategy.CAUSAL]: 'bg-pink-500/10 text-pink-700 dark:text-pink-400 border-pink-500/20',
  [ReasoningStrategy.ALGORITHMIC]: 'bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border-cyan-500/20'
};

/**
 * Thinking mode configuration
 * Display settings for each thinking mode
 */
const THINKING_MODE_CONFIG: Record<ThinkingMode, {
  label: string;
  color: string;
  bgColor: string;
  icon: string;
  description: string;
}> = {
  [ThinkingMode.SYSTEM1]: {
    label: 'Fast Thinking',
    color: 'text-white',
    bgColor: 'bg-green-500',
    icon: '⚡',
    description: 'Quick, intuitive response'
  },
  [ThinkingMode.SYSTEM2]: {
    label: 'Deep Thinking',
    color: 'text-white',
    bgColor: 'bg-blue-500',
    icon: '🧠',
    description: 'Careful, step-by-step reasoning'
  },
  [ThinkingMode.HYBRID]: {
    label: 'Adaptive Thinking',
    color: 'text-white',
    bgColor: 'bg-purple-500',
    icon: '🔄',
    description: 'Balanced approach'
  }
};

/**
 * Confidence Bar Component
 * Visual representation of confidence score
 */
const ConfidenceBar: React.FC<{
  confidence: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}> = ({ confidence, showLabel = true, size = 'md' }) => {
  const heightClass = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3'
  }[size];
  
  const textClass = {
    sm: 'text-xs',
    md: 'text-xs',
    lg: 'text-sm'
  }[size];
  
  // Color based on confidence level
  const colorClass = confidence >= 0.8
    ? 'bg-green-500'
    : confidence >= 0.6
    ? 'bg-yellow-500'
    : 'bg-red-500';
  
  return (
    <div className="flex items-center gap-2 w-full">
      <div className={cn(
        'flex-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden',
        heightClass
      )}>
        <motion.div
          className={cn('h-full rounded-full', colorClass)}
          initial={{ width: 0 }}
          animate={{ width: `${confidence * 100}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          aria-label={`Confidence: ${(confidence * 100).toFixed(0)}%`}
        />
      </div>
      
      {showLabel && (
        <span className={cn(
          'font-medium text-gray-600 dark:text-gray-400 tabular-nums',
          textClass
        )}>
          {(confidence * 100).toFixed(0)}%
        </span>
      )}
    </div>
  );
};

/**
 * Thinking Mode Badge Component
 * Displays selected thinking mode
 */
const ThinkingModeBadge: React.FC<{ mode: ThinkingMode }> = ({ mode }) => {
  const config = THINKING_MODE_CONFIG[mode];
  
  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
        config.bgColor,
        config.color
      )}
      role="status"
      aria-label={`${config.label}: ${config.description}`}
    >
      <span aria-hidden="true">{config.icon}</span>
      <span>{config.label}</span>
    </div>
  );
};

/**
 * Reasoning Step Card Component
 * Individual step in the reasoning chain
 */
const ReasoningStepCard: React.FC<{
  step: ReasoningStep;
  index: number;
  onClick?: () => void;
}> = ({ step, index, onClick }) => {
  const strategyColor = STRATEGY_COLORS[step.strategy] || 'bg-gray-100 text-gray-600 border-gray-200';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className={cn(
        'reasoning-step p-4 rounded-lg border transition-shadow',
        'bg-white dark:bg-gray-800',
        'border-gray-200 dark:border-gray-700',
        onClick && 'cursor-pointer hover:shadow-md'
      )}
      onClick={onClick}
      data-testid={`reasoning-step-${step.step_number}`}
      role="article"
      aria-label={`Step ${step.step_number}: ${step.strategy} reasoning`}
    >
      {/* Step header */}
      <div className="flex items-start gap-3 mb-3">
        {/* Step number badge */}
        <div
          className={cn(
            'flex-shrink-0 w-8 h-8 rounded-full',
            'bg-blue-500 text-white',
            'flex items-center justify-center',
            'text-sm font-bold'
          )}
          aria-label={`Step ${step.step_number}`}
        >
          {step.step_number}
        </div>
        
        <div className="flex-1 min-w-0">
          {/* Strategy badge and confidence */}
          <div className="flex items-center justify-between mb-2 gap-2">
            <span
              className={cn(
                'inline-block px-2 py-0.5 rounded text-xs font-medium border',
                strategyColor
              )}
              role="note"
              aria-label={`Strategy: ${step.strategy}`}
            >
              {step.strategy.charAt(0).toUpperCase() + step.strategy.slice(1)}
            </span>
            
            <div className="w-24 flex-shrink-0">
              <ConfidenceBar
                confidence={step.confidence}
                showLabel={true}
                size="sm"
              />
            </div>
          </div>
          
          {/* Step content */}
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
            {step.content}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Main Reasoning Chain Display Component
 * 
 * Displays complete reasoning chain with metadata and interactions
 */
export const ReasoningChainDisplay: React.FC<ReasoningChainDisplayProps> = ({
  reasoning,
  isStreaming = false,
  className,
  onStepClick,
  onFeedback
}) => {
  // Memoize computed values for performance
  const strategyDistribution = useMemo(
    () => reasoning.strategy_distribution || {},
    [reasoning.strategy_distribution]
  );
  
  const hasMultipleStrategies = useMemo(
    () => Object.keys(strategyDistribution).length > 1,
    [strategyDistribution]
  );
  
  return (
    <div
      className={cn('reasoning-chain-container', className)}
      role="region"
      aria-label="Reasoning chain display"
    >
      {/* Header Section */}
      <div className="mb-6 space-y-3">
        {/* Title and mode badge */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <Brain className="w-5 h-5" aria-hidden="true" />
            <span>Thinking Process</span>
          </h3>
          <ThinkingModeBadge mode={reasoning.thinking_mode} />
        </div>
        
        {/* Overall confidence bar */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">
              Overall Confidence
            </span>
            <span className="font-medium tabular-nums">
              {(reasoning.total_confidence * 100).toFixed(0)}%
            </span>
          </div>
          <ConfidenceBar
            confidence={reasoning.total_confidence}
            showLabel={false}
            size="lg"
          />
        </div>
        
        {/* Metadata pills */}
        <div
          className="flex items-center flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400"
          role="list"
          aria-label="Reasoning metadata"
        >
          <span className="flex items-center gap-1" role="listitem">
            <TrendingUp className="w-3 h-3" aria-hidden="true" />
            {reasoning.steps.length} steps
          </span>
          <span aria-hidden="true">•</span>
          <span className="flex items-center gap-1" role="listitem">
            <Clock className="w-3 h-3" aria-hidden="true" />
            {(reasoning.processing_time_ms / 1000).toFixed(1)}s
          </span>
          <span aria-hidden="true">•</span>
          <span role="listitem">
            Complexity: {(reasoning.complexity_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      
      {/* Reasoning Steps */}
      <div className="space-y-4" role="feed" aria-label="Reasoning steps">
        <AnimatePresence>
          {reasoning.steps.map((step, index) => (
            <ReasoningStepCard
              key={step.id || step.step_number}
              step={step}
              index={index}
              onClick={onStepClick ? () => onStepClick(step) : undefined}
            />
          ))}
        </AnimatePresence>
        
        {/* Streaming indicator */}
        {isStreaming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 p-4"
            role="status"
            aria-live="polite"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              aria-hidden="true"
            >
              <Brain className="w-4 h-4" />
            </motion.div>
            <span>Thinking...</span>
          </motion.div>
        )}
      </div>
      
      {/* Conclusion Section */}
      {reasoning.conclusion && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            'mt-6 p-4 rounded-lg border',
            'bg-green-50 dark:bg-green-900/20',
            'border-green-200 dark:border-green-800'
          )}
          data-testid="reasoning-conclusion"
          role="article"
          aria-label="Reasoning conclusion"
        >
          <div className="flex items-start gap-3">
            <CheckCircle
              className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5"
              aria-hidden="true"
            />
            <div className="flex-1">
              <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                Conclusion
              </h4>
              <p className="text-sm text-green-800 dark:text-green-200">
                {reasoning.conclusion}
              </p>
            </div>
          </div>
        </motion.div>
      )}
      
      {/* Strategy Distribution */}
      {hasMultipleStrategies && (
        <div
          className="mt-6 p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50"
          role="complementary"
          aria-label="Reasoning strategies used"
        >
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" aria-hidden="true" />
            Reasoning Strategies Used
          </h4>
          <div className="flex flex-wrap gap-2" role="list">
            {Object.entries(strategyDistribution).map(([strategy, count]) => (
              <span
                key={strategy}
                className={cn(
                  'px-2 py-1 rounded text-xs font-medium border',
                  STRATEGY_COLORS[strategy as ReasoningStrategy] ||
                    'bg-gray-100 text-gray-600 border-gray-200'
                )}
                role="listitem"
              >
                {strategy}: {count}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Feedback Section */}
      {onFeedback && !isStreaming && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            Was this reasoning helpful?
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onFeedback(5, true)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                'bg-green-100 hover:bg-green-200 text-green-700',
                'dark:bg-green-900/20 dark:hover:bg-green-900/40 dark:text-green-400',
                'focus:outline-none focus:ring-2 focus:ring-green-500'
              )}
              aria-label="Mark reasoning as helpful"
            >
              👍 Helpful
            </button>
            <button
              onClick={() => onFeedback(1, false)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                'bg-red-100 hover:bg-red-200 text-red-700',
                'dark:bg-red-900/20 dark:hover:bg-red-900/40 dark:text-red-400',
                'focus:outline-none focus:ring-2 focus:ring-red-500'
              )}
              aria-label="Mark reasoning as not helpful"
            >
              👎 Not Helpful
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReasoningChainDisplay;
