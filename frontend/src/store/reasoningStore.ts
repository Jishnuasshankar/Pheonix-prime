/**
 * Reasoning Zustand Store
 * 
 * Centralized state management for Deep Thinking / Reasoning features
 * 
 * AGENTS_FRONTEND.md compliant:
 * - Centralized state for shared data
 * - Immutable state updates
 * - TypeScript strict mode
 * - State persistence strategy
 * - Zero 'any' types
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  ReasoningChain,
  ReasoningDisplayPreferences,
  ReasoningStoreState
} from '@/types/reasoning.types';

/**
 * Default display preferences
 */
const DEFAULT_PREFERENCES: ReasoningDisplayPreferences = {
  showReasoningByDefault: true,
  autoExpandSteps: true,
  showConfidence: true,
  showStrategy: true,
  showTiming: true,
  animationSpeed: 1,
  compactMode: false
};

/**
 * Reasoning store initial state
 */
const initialState = {
  currentChain: null,
  chains: {},
  isLoading: false,
  error: null,
  preferences: DEFAULT_PREFERENCES
};

/**
 * Reasoning store
 * 
 * Manages state for reasoning chains, display preferences, and loading states.
 * Persists preferences to localStorage for user convenience.
 * 
 * @example
 * ```typescript
 * const { currentChain, setCurrentChain, preferences } = useReasoningStore();
 * 
 * // Set current reasoning chain
 * setCurrentChain(newChain);
 * 
 * // Update preferences
 * setPreferences({ showConfidence: false });
 * ```
 */
export const useReasoningStore = create<ReasoningStoreState>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      /**
       * Set current reasoning chain being displayed
       * 
       * @param chain - Reasoning chain to display (or null to clear)
       */
      setCurrentChain: (chain: ReasoningChain | null) => {
        set({ currentChain: chain });
      },
      
      /**
       * Add reasoning chain to history
       * 
       * Stores chain in session-specific history for later retrieval.
       * Maintains immutability by creating new objects.
       * 
       * @param sessionId - Session identifier
       * @param chain - Reasoning chain to add
       */
      addChain: (sessionId: string, chain: ReasoningChain) => {
        set((state) => {
          const existingChains = state.chains[sessionId] || [];
          
          // Check if chain already exists (by ID)
          const chainExists = existingChains.some((c) => c.id === chain.id);
          
          if (chainExists) {
            // Update existing chain
            return {
              chains: {
                ...state.chains,
                [sessionId]: existingChains.map((c) =>
                  c.id === chain.id ? chain : c
                )
              }
            };
          }
          
          // Add new chain
          return {
            chains: {
              ...state.chains,
              [sessionId]: [...existingChains, chain]
            }
          };
        });
      },
      
      /**
       * Update existing reasoning chain
       * 
       * Applies partial updates to a chain (e.g., adding steps, updating conclusion).
       * Maintains immutability.
       * 
       * @param chainId - Chain identifier
       * @param updates - Partial chain updates
       */
      updateChain: (chainId: string, updates: Partial<ReasoningChain>) => {
        set((state) => {
          // Find session containing this chain
          const sessionId = Object.keys(state.chains).find((sid) =>
            state.chains[sid]?.some((c) => c.id === chainId)
          );
          
          if (!sessionId) {
            console.warn(`[ReasoningStore] Chain ${chainId} not found`);
            return state;
          }
          
          const sessionChains = state.chains[sessionId];
          
          return {
            chains: {
              ...state.chains,
              [sessionId]: sessionChains.map((c) =>
                c.id === chainId ? { ...c, ...updates } : c
              )
            },
            // Update currentChain if it's the one being updated
            currentChain:
              state.currentChain?.id === chainId
                ? { ...state.currentChain, ...updates }
                : state.currentChain
          };
        });
      },
      
      /**
       * Clear reasoning chains
       * 
       * Clears all chains for a specific session, or all chains if no session specified.
       * 
       * @param sessionId - Optional session identifier (clears all if omitted)
       */
      clearChains: (sessionId?: string) => {
        set((state) => {
          if (sessionId) {
            // Clear specific session
            const { [sessionId]: removed, ...remainingChains } = state.chains;
            
            return {
              chains: remainingChains,
              // Clear currentChain if it belongs to cleared session
              currentChain:
                state.currentChain &&
                state.chains[sessionId]?.some(
                  (c) => c.id === state.currentChain?.id
                )
                  ? null
                  : state.currentChain
            };
          }
          
          // Clear all chains
          return {
            chains: {},
            currentChain: null
          };
        });
      },
      
      /**
       * Update display preferences
       * 
       * Applies partial updates to preferences.
       * Preferences are persisted to localStorage.
       * 
       * @param preferences - Partial preference updates
       */
      setPreferences: (preferences: Partial<ReasoningDisplayPreferences>) => {
        set((state) => ({
          preferences: {
            ...state.preferences,
            ...preferences
          }
        }));
      },
      
      /**
       * Set error state
       * 
       * @param error - Error message (or null to clear)
       */
      setError: (error: string | null) => {
        set({ error });
      },
      
      /**
       * Reset store to initial state
       * 
       * Clears all chains and resets preferences to defaults.
       * Useful for logout or testing.
       */
      reset: () => {
        set(initialState);
      }
    }),
    {
      name: 'masterx-reasoning-store',
      storage: createJSONStorage(() => localStorage),
      
      // Only persist preferences, not temporary data like chains
      partialize: (state) => ({
        preferences: state.preferences
      })
    }
  )
);

/**
 * Selectors for optimized component access
 * 
 * These selectors allow components to subscribe to specific parts of state,
 * preventing unnecessary re-renders.
 */

/**
 * Select current reasoning chain
 */
export const selectCurrentChain = (state: ReasoningStoreState) =>
  state.currentChain;

/**
 * Select chains for specific session
 */
export const selectSessionChains = (sessionId: string) => (
  state: ReasoningStoreState
) => state.chains[sessionId] || [];

/**
 * Select display preferences
 */
export const selectPreferences = (state: ReasoningStoreState) =>
  state.preferences;

/**
 * Select error state
 */
export const selectError = (state: ReasoningStoreState) => state.error;

/**
 * Select loading state
 */
export const selectIsLoading = (state: ReasoningStoreState) => state.isLoading;

/**
 * Select specific preference
 */
export const selectPreference = <K extends keyof ReasoningDisplayPreferences>(
  key: K
) => (state: ReasoningStoreState) => state.preferences[key];

/**
 * Export store hook and selectors
 */
export default useReasoningStore;
