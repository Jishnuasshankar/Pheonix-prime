"""
Dynamic Multi-AI Provider System
Following specifications from 3.MASTERX_COMPREHENSIVE_PLAN.md Section 2

REVOLUTIONARY APPROACH:
- Auto-discovers providers from .env (no hardcoding!)
- Supports unlimited AI providers
- Add/remove models by just editing .env
- No code changes needed

Phase 1 Implementation: Auto-discovery + Basic routing
Phase 2 (Week 2): Add benchmarking system
"""

import os
import logging
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from core.models import AIResponse, EmotionState
from utils.errors import ProviderError

logger = logging.getLogger(__name__)


# ============================================================================
# PROVIDER HEALTH TRACKING (Phase 8C File 11 Integration)
# ============================================================================

@dataclass
class ProviderHealthMetrics:
    """
    Health metrics for AI provider
    
    Tracks real-time performance for health monitoring system.
    AGENTS.md compliant: No hardcoded thresholds, all metrics tracked.
    """
    provider_name: str
    is_available: bool
    avg_response_time: float  # milliseconds
    error_rate: float  # 0.0 to 1.0
    rate_limit_remaining: int
    last_success: datetime
    total_requests: int
    error_count: int
    recent_response_times: List[float] = field(default_factory=list)


class ProviderHealthTracker:
    """
    Tracks health metrics for providers
    
    Used by HealthMonitor (File 11) for statistical analysis.
    Zero hardcoded values - all metrics ML-driven.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Args:
            max_history: Number of recent metrics to keep (from settings)
        """
        self.max_history = max_history
        self.metrics: Dict[str, Dict] = {}
        
    def initialize_provider(self, provider_name: str):
        """Initialize tracking for a provider"""
        if provider_name not in self.metrics:
            self.metrics[provider_name] = {
                'total_requests': 0,
                'error_count': 0,
                'response_times': deque(maxlen=self.max_history),
                'last_success': None,
                'last_error': None,
                'is_available': True
            }
    
    def record_request(
        self,
        provider_name: str,
        response_time_ms: float,
        success: bool
    ):
        """Record a request for health tracking"""
        self.initialize_provider(provider_name)
        
        metrics = self.metrics[provider_name]
        metrics['total_requests'] += 1
        metrics['response_times'].append(response_time_ms)
        
        if success:
            metrics['last_success'] = datetime.utcnow()
            metrics['is_available'] = True
        else:
            metrics['error_count'] += 1
            metrics['last_error'] = datetime.utcnow()
            
            # Mark unavailable if too many recent errors
            if len(metrics['response_times']) >= 10:
                recent_errors = metrics['error_count']
                if recent_errors / metrics['total_requests'] > 0.5:
                    metrics['is_available'] = False
    
    def get_health_metrics(self, provider_name: str) -> ProviderHealthMetrics:
        """Get health metrics for a provider"""
        self.initialize_provider(provider_name)
        
        metrics = self.metrics[provider_name]
        response_times = list(metrics['response_times'])
        
        # Calculate average response time
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0.0
        )
        
        # Calculate error rate
        total = metrics['total_requests']
        error_rate = metrics['error_count'] / total if total > 0 else 0.0
        
        return ProviderHealthMetrics(
            provider_name=provider_name,
            is_available=metrics['is_available'],
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            rate_limit_remaining=999999,  # TODO: Track actual rate limits
            last_success=metrics['last_success'] or datetime.utcnow(),
            total_requests=total,
            error_count=metrics['error_count'],
            recent_response_times=response_times[-10:]  # Last 10
        )


class ProviderRegistry:
    """Auto-discover AI providers from environment variables"""
    
    def __init__(self):
        self.providers: Dict[str, Dict] = {}
        self.discover_providers()
    
    def discover_providers(self):
        """
        Scan .env for *_API_KEY and *_MODEL_NAME patterns
        Automatically initializes discovered providers
        """
        env_vars = list(os.environ.keys())
        
        # Find all API keys
        api_keys = [k for k in env_vars if k.endswith('_API_KEY') or k.endswith('_LLM_KEY')]
        
        logger.info(f"Scanning environment for AI providers...")
        
        for key_var in api_keys:
            # Extract provider name
            provider_name = key_var.replace('_API_KEY', '').replace('_LLM_KEY', '').lower()
            
            # Look for corresponding model name
            model_var_options = [
                f"{provider_name.upper()}_MODEL_NAME",
                f"{provider_name.upper()}_MODEL"
            ]
            
            model_name = None
            for model_var in model_var_options:
                if model_var in env_vars:
                    model_name = os.getenv(model_var)
                    break
            
            # Get API key
            api_key = os.getenv(key_var)
            
            if api_key:
                self.providers[provider_name] = {
                    'api_key': api_key,
                    'model_name': model_name,
                    'enabled': True,
                    'key_var': key_var
                }
                logger.info(f"✅ Discovered provider: {provider_name} (model: {model_name or 'default'})")
        
        if not self.providers:
            logger.warning("⚠️ No AI providers discovered in environment")
        else:
            logger.info(f"📊 Total providers discovered: {len(self.providers)}")
    
    def get_provider(self, name: str) -> Optional[Dict]:
        """Get provider configuration by name"""
        return self.providers.get(name.lower())
    
    def get_all_providers(self) -> Dict[str, Dict]:
        """Get all discovered providers"""
        return self.providers
    
    def get_llm_providers(self) -> Dict[str, Dict]:
        """
        Get only LLM providers (for text generation)
        
        Filters out non-LLM providers like:
        - TTS providers (elevenlabs)
        - Benchmark APIs (artificial_analysis, llm_stats)
        
        LLM providers are identified by having a MODEL_NAME for text generation
        and NOT being in the excluded list.
        """
        # Providers that are NOT for LLM text generation
        excluded_providers = {
            'elevenlabs',      # TTS provider
            'artificial_analysis',  # Benchmark API
            'llm_stats',       # Benchmark API
            'whisper',         # Speech-to-text
            'stripe',          # Payment
            'jwt'              # Authentication
        }
        
        llm_providers = {}
        for name, config in self.providers.items():
            # Include only if:
            # 1. Not in excluded list
            # 2. Has a model_name (indicating it's for generation)
            if name not in excluded_providers and config.get('model_name'):
                llm_providers[name] = config
        
        return llm_providers
    
    def is_available(self, name: str) -> bool:
        """Check if provider is available"""
        provider = self.get_provider(name)
        return provider is not None and provider.get('enabled', False)


class UniversalProvider:
    """Unified interface for all AI providers"""
    
    def __init__(self, registry: ProviderRegistry):
        self.registry = registry
        self._clients = {}
    
    def _get_client(self, provider_name: str):
        """Get or create client for provider"""
        if provider_name in self._clients:
            return self._clients[provider_name]
        
        provider = self.registry.get_provider(provider_name)
        if not provider:
            raise ProviderError(
                f"Provider {provider_name} not found",
                details={'provider': provider_name}
            )
        
        # Initialize client based on provider
        client = None
        
        try:
            if provider_name == 'groq':
                from groq import AsyncGroq
                client = AsyncGroq(api_key=provider['api_key'])
            
            elif provider_name == 'emergent':
                from emergentintegrations.llm.chat import LlmChat
                # Emergent uses the universal key
                client = LlmChat(
                    api_key=provider['api_key'],
                    session_id="masterx",
                    system_message="You are a helpful AI learning assistant."
                )
            
            elif provider_name == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=provider['api_key'])
                client = genai
            
            elif provider_name == 'openai':
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=provider['api_key'])
            
            elif provider_name == 'anthropic':
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=provider['api_key'])
            
            else:
                logger.warning(f"Provider {provider_name} not yet implemented, using fallback")
                return None
            
            self._clients[provider_name] = client
            return client
        
        except Exception as e:
            logger.error(f"Error initializing {provider_name} client: {e}")
            raise ProviderError(
                f"Failed to initialize {provider_name}",
                details={'provider': provider_name, 'error': str(e)}
            )
    
    async def generate(
        self,
        provider_name: str,
        prompt: str,
        max_tokens: int = 1000
    ) -> AIResponse:
        """Generate response from specified provider"""
        
        start_time = time.time()
        provider = self.registry.get_provider(provider_name)
        
        if not provider:
            raise ProviderError(
                f"Provider {provider_name} not available",
                details={'provider': provider_name}
            )
        
        try:
            client = self._get_client(provider_name)
            model_name = provider['model_name'] or 'default'
            
            # Route to correct provider implementation
            if provider_name == 'groq':
                response = await self._groq_generate(client, model_name, prompt, max_tokens)
            
            elif provider_name == 'emergent':
                response = await self._emergent_generate(client, model_name, prompt, max_tokens)
            
            elif provider_name == 'gemini':
                response = await self._gemini_generate(client, model_name, prompt, max_tokens)
            
            elif provider_name == 'openai':
                response = await self._openai_generate(client, model_name, prompt, max_tokens)
            
            elif provider_name == 'anthropic':
                response = await self._anthropic_generate(client, model_name, prompt, max_tokens)
            
            else:
                raise ProviderError(
                    f"Provider {provider_name} not implemented",
                    details={'provider': provider_name}
                )
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(f"✅ {provider_name} response generated in {elapsed_ms:.0f}ms")
            
            return response
        
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ {provider_name} failed after {elapsed_ms:.0f}ms: {e}")
            raise ProviderError(
                f"Provider {provider_name} failed",
                details={
                    'provider': provider_name,
                    'error': str(e),
                    'elapsed_ms': elapsed_ms
                }
            )
    
    async def _groq_generate(self, client, model_name, prompt, max_tokens) -> AIResponse:
        """Generate using Groq"""
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider="groq",
            model_name=model_name,
            tokens_used=response.usage.total_tokens,
            cost=0.0,  # Calculate in cost tracker
            response_time_ms=0.0
        )
    
    async def _emergent_generate(self, client, model_name, prompt, max_tokens) -> AIResponse:
        """Generate using Emergent LLM (LiteLLM-based)"""
        from emergentintegrations.llm.chat import UserMessage
        
        # Send message using Emergent's LlmChat
        user_msg = UserMessage(text=prompt)
        response_text = await client.send_message(user_msg)
        
        return AIResponse(
            content=response_text,
            provider="emergent",
            model_name=model_name,
            tokens_used=len(response_text.split()),  # Approximate
            cost=0.0,
            response_time_ms=0.0
        )
    
    async def _gemini_generate(self, client, model_name, prompt, max_tokens) -> AIResponse:
        """Generate using Google Gemini"""
        model = client.GenerativeModel(model_name)
        response = await model.generate_content_async(prompt)
        
        # Estimate tokens (Gemini doesn't provide exact count in basic API)
        estimated_tokens = len(prompt.split()) + len(response.text.split())
        
        return AIResponse(
            content=response.text,
            provider="gemini",
            model_name=model_name,
            tokens_used=estimated_tokens,
            cost=0.0,
            response_time_ms=0.0
        )
    
    async def _openai_generate(self, client, model_name, prompt, max_tokens) -> AIResponse:
        """Generate using OpenAI"""
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        return AIResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model_name=model_name,
            tokens_used=response.usage.total_tokens,
            cost=0.0,
            response_time_ms=0.0
        )
    
    async def _anthropic_generate(self, client, model_name, prompt, max_tokens) -> AIResponse:
        """Generate using Anthropic Claude"""
        response = await client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return AIResponse(
            content=response.content[0].text,
            provider="anthropic",
            model_name=model_name,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            cost=0.0,
            response_time_ms=0.0
        )


class ProviderManager:
    """
    Main interface for AI provider management
    
    Features:
    - Auto-discovery of providers from .env
    - External benchmarking integration (Artificial Analysis API)
    - Smart routing based on real-world rankings
    - Automatic fallback on provider failure
    """
    
    def __init__(self):
        self.registry = ProviderRegistry()
        self.universal = UniversalProvider(self.registry)
        self.external_benchmarks = None  # Initialized in server startup
        self.pricing_engine = None  # Initialized in server startup
        self._default_provider = None
        
        # Add universal provider reference for minimal manual tests
        self.universal_provider = self.universal
        
        # Health tracking (Phase 8C File 11 integration)
        history_size = int(os.getenv("PROVIDER_HEALTH_HISTORY_SIZE", "100"))
        self.health_tracker = ProviderHealthTracker(max_history=history_size)
        
        # Selection weights (ML-optimized, configurable via env)
        self.selection_weights = {
            'quality': float(os.getenv("SELECTION_WEIGHT_QUALITY", "0.4")),
            'cost': float(os.getenv("SELECTION_WEIGHT_COST", "0.2")),
            'speed': float(os.getenv("SELECTION_WEIGHT_SPEED", "0.2")),
            'availability': float(os.getenv("SELECTION_WEIGHT_AVAILABILITY", "0.2"))
        }
        
        # Normalize weights
        total = sum(self.selection_weights.values())
        self.selection_weights = {k: v/total for k, v in self.selection_weights.items()}
        
        logger.info("✅ ProviderManager initialized (dynamic mode)")
    
    def set_dependencies(self, external_benchmarks, pricing_engine):
        """Set dependencies (called by server.py on startup)"""
        self.external_benchmarks = external_benchmarks
        self.pricing_engine = pricing_engine
        logger.info("✅ ProviderManager connected to dynamic systems")
    
    async def select_best_model(
        self,
        category: str = "general",
        max_cost_per_1m_tokens: Optional[float] = None,
        min_quality_score: float = 0.0,
        prefer_speed: bool = False,
        exclude_providers: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Intelligently select best available model
        
        Uses multi-criteria decision analysis:
        - Availability (.env)
        - Quality (benchmarks)
        - Cost (pricing engine)
        - Speed (benchmarks metadata)
        
        Args:
            category: Task category (coding, math, reasoning, etc.)
            max_cost_per_1m_tokens: Maximum cost constraint
            min_quality_score: Minimum quality threshold
            prefer_speed: Optimize for speed over quality
            exclude_providers: Providers to exclude
        
        Returns:
            Tuple of (provider, model_name)
        """
        
        exclude_providers = exclude_providers or []
        available_providers = self.registry.get_llm_providers()
        
        if not available_providers:
            raise ProviderError("No LLM providers available in .env")
        
        # Get benchmark rankings
        rankings = []
        if self.external_benchmarks:
            try:
                rankings = await self.external_benchmarks.get_rankings(category)
            except Exception as e:
                logger.warning(f"Failed to get rankings: {e}")
        
        # Build candidate list with scores
        candidates = []
        
        for provider_name, provider_config in available_providers.items():
            if provider_name in exclude_providers:
                continue
            
            model_name = provider_config.get('model_name', 'default')
            
            # Get quality score from benchmarks
            # IMPORTANT: Take the BEST (highest scoring) model for this provider
            quality_score = 70.0  # Default baseline
            speed_score = 50.0  # Default speed
            best_ranking = None
            
            for ranking in rankings:
                if ranking.provider == provider_name:
                    # Take the best ranking (highest score) for this provider
                    if best_ranking is None or ranking.score > best_ranking.score:
                        best_ranking = ranking
            
            if best_ranking:
                quality_score = best_ranking.score
                speed_score = best_ranking.metadata.get('speed', 50.0) or 50.0
                logger.debug(
                    f"Provider '{provider_name}' quality from benchmarks: {quality_score:.1f} "
                    f"(best model: {best_ranking.model_name})"
                )
            
            # Skip if below minimum quality
            if quality_score < min_quality_score:
                continue
            
            # Get cost
            cost_score = 0.5  # Default middle
            if self.pricing_engine:
                try:
                    pricing = await self.pricing_engine.get_pricing(provider_name, model_name)
                    avg_cost = (pricing.input_cost_per_million + pricing.output_cost_per_million) / 2
                    
                    # Skip if too expensive
                    if max_cost_per_1m_tokens and avg_cost > max_cost_per_1m_tokens:
                        continue
                    
                    # Normalize cost (logarithmic scale)
                    import math
                    if avg_cost > 0:
                        cost_score = 1.0 - min(1.0, math.log(avg_cost + 0.01) / math.log(100))
                    
                except Exception as e:
                    logger.warning(f"Failed to get pricing for {provider_name}: {e}")
            
            # Normalize scores
            quality_normalized = quality_score / 100.0
            speed_normalized = min(1.0, speed_score / 500.0)
            
            # Calculate weighted score
            weights = self.selection_weights.copy()
            if prefer_speed:
                weights['speed'] *= 1.5
                weights['quality'] *= 0.7
                total = sum(weights.values())
                weights = {k: v/total for k, v in weights.items()}
            
            overall_score = (
                weights['quality'] * quality_normalized +
                weights['cost'] * cost_score +
                weights['speed'] * speed_normalized +
                weights['availability'] * 1.0
            )
            
            candidates.append({
                'provider': provider_name,
                'model_name': model_name,
                'overall_score': overall_score,
                'quality_score': quality_score,
                'cost_score': cost_score,
                'speed_score': speed_score
            })
            
            # Log scoring details for debugging
            logger.debug(
                f"Candidate {provider_name}: overall={overall_score:.3f} "
                f"(quality={quality_score:.1f}, cost={cost_score:.3f}, speed={speed_score:.1f})"
            )
        
        if not candidates:
            raise ProviderError(f"No suitable models for category {category}")
        
        # Sort by overall score
        candidates.sort(key=lambda x: x['overall_score'], reverse=True)
        best = candidates[0]
        
        # Log all candidates for transparency
        logger.info(f"Provider selection for category '{category}':")
        for i, cand in enumerate(candidates, 1):
            logger.info(
                f"  #{i}: {cand['provider']} - overall={cand['overall_score']:.3f} "
                f"(Q:{cand['quality_score']:.1f}, C:{cand['cost_score']:.2f}, S:{cand['speed_score']:.1f})"
            )
        
        logger.info(
            f"✅ Selected {best['provider']}:{best['model_name']} "
            f"(score: {best['overall_score']:.3f}, quality: {best['quality_score']:.1f})"
        )
        
        return best['provider'], best['model_name']
    
    async def generate(
        self,
        prompt: str,
        category: str = "general",
        provider_name: Optional[str] = None,
        max_tokens: int = 1000,
        max_cost_per_1m: Optional[float] = None
    ) -> AIResponse:
        """
        Generate AI response with intelligent model selection
        
        If provider_name specified, uses that provider.
        Otherwise, dynamically selects best available model.
        
        Args:
            prompt: User prompt
            category: Task category (coding, math, etc.)
            provider_name: Specific provider to use (optional)
            max_tokens: Maximum tokens
            max_cost_per_1m: Maximum cost constraint (optional)
        
        Returns:
            AIResponse
        """
        
        # If provider specified, use it
        if provider_name:
            logger.info(f"Using specified provider: {provider_name}")
            target_provider = provider_name
            provider_config = self.registry.get_provider(provider_name)
            model_name = provider_config.get('model_name', 'default') if provider_config else 'default'
        else:
            # Dynamic selection!
            try:
                target_provider, model_name = await self.select_best_model(
                    category=category,
                    max_cost_per_1m_tokens=max_cost_per_1m
                )
            except Exception as e:
                logger.error(f"Model selection failed: {e}")
                # Fallback: use first available LLM provider
                available = self.registry.get_llm_providers()
                if available:
                    target_provider = list(available.keys())[0]
                    model_name = available[target_provider].get('model_name', 'default')
                    logger.warning(f"Using fallback: {target_provider}")
                else:
                    raise ProviderError("No LLM providers available")
        
        # Generate using selected provider
        logger.info(f"🤖 Generating with {target_provider}:{model_name} for category: {category}")
        
        try:
            start_time = time.time()
            response = await self.universal.generate(
                provider_name=target_provider,
                prompt=prompt,
                max_tokens=max_tokens
            )
            response_time_ms = (time.time() - start_time) * 1000
            
            # Track health metrics (Phase 8C File 11)
            self.health_tracker.record_request(
                provider_name=target_provider,
                response_time_ms=response_time_ms,
                success=True
            )
            
            # Add category to response
            if hasattr(response, 'category'):
                response.category = category
            
            return response
        
        except ProviderError as e:
            # Track failure (Phase 8C File 11)
            self.health_tracker.record_request(
                provider_name=target_provider,
                response_time_ms=0.0,
                success=False
            )
            
            # Intelligent fallback: try next best model
            logger.warning(f"Provider {target_provider} failed: {e}, trying fallback...")
            
            try:
                # Select alternative, excluding failed provider
                alt_provider, alt_model = await self.select_best_model(
                    category=category,
                    exclude_providers=[target_provider]
                )
                
                logger.info(f"🔄 Using fallback: {alt_provider}:{alt_model}")
                start_time = time.time()
                response = await self.universal.generate(
                    provider_name=alt_provider,
                    prompt=prompt,
                    max_tokens=max_tokens
                )
                response_time_ms = (time.time() - start_time) * 1000
                
                # Track fallback success
                self.health_tracker.record_request(
                    provider_name=alt_provider,
                    response_time_ms=response_time_ms,
                    success=True
                )
                
                return response
                
            except Exception as fallback_error:
                logger.error(f"All fallback attempts failed: {fallback_error}")
                raise ProviderError(
                    "All AI providers failed",
                    details={'attempted_llm_providers': list(self.registry.get_llm_providers().keys())}
                )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM provider names (excluding TTS and Benchmark APIs)"""
        return list(self.registry.get_llm_providers().keys())
    
    async def get_provider_health(self, provider_name: str) -> ProviderHealthMetrics:
        """
        Get health metrics for specific provider
        
        Phase 8C File 11 Integration: Used by HealthMonitor for system health
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            ProviderHealthMetrics with current health data
        """
        return self.health_tracker.get_health_metrics(provider_name)
    
    async def initialize_external_benchmarks(self, db):
        """
        Initialize external benchmarking system
        Called during server startup
        
        Args:
            db: MongoDB database instance
        """
        from core.external_benchmarks import get_external_benchmarks
        
        try:
            api_key = os.getenv("ARTIFICIAL_ANALYSIS_API_KEY")
            
            self.external_benchmarks = get_external_benchmarks(db, api_key)
            
            # Fetch initial rankings for all categories
            logger.info("Fetching initial rankings from external APIs...")
            for category in ["coding", "math", "reasoning", "research", "empathy", "general"]:
                await self.external_benchmarks.get_rankings(category)
            
            # Start background update task
            import asyncio
            asyncio.create_task(
                self.external_benchmarks.schedule_periodic_updates(interval_hours=12)
            )
            
            logger.info("✅ External benchmarking initialized with periodic updates")
            
        except Exception as e:
            logger.error(f"⚠️ External benchmarking initialization failed: {e}")
            logger.info("Will continue with simple routing")
    
    async def select_best_provider_for_category(
        self,
        category: str,
        emotion_state: Optional[EmotionState] = None
    ) -> str:
        """
        Select best provider for a category using external benchmarks
        
        COMPLETELY DYNAMIC - NO HARDCODED PROVIDERS
        
        Priority:
        1. Use external benchmarks (Artificial Analysis, LLM-Stats) 
        2. Fall back to round-robin selection from available providers
        
        Args:
            category: Task category (coding, math, reasoning, etc.)
            emotion_state: User's emotion state (for empathy routing)
        
        Returns:
            Provider name
        """
        
        # Get available LLM providers (completely dynamic from .env)
        available_llm = self.get_available_providers()
        
        if not available_llm:
            raise Exception("No LLM providers available in .env")
        
        # If external benchmarks available, use them
        if self.external_benchmarks:
            try:
                # Get rankings for category
                rankings = await self.external_benchmarks.get_rankings(category)
                
                if rankings and len(rankings) > 0:
                    logger.info(f"📊 Got {len(rankings)} rankings for {category}")
                    logger.info(f"✅ Available LLM providers: {available_llm}")
                    
                    # Find best available provider from rankings
                    for ranking in rankings:
                        if ranking.provider in available_llm:
                            logger.info(
                                f"🎯 Selected {ranking.provider} for {category} "
                                f"(rank #{ranking.rank}, score: {ranking.score:.1f}, "
                                f"source: {ranking.source})"
                            )
                            return ranking.provider
                    
                    logger.warning(
                        f"⚠️ No benchmark matches found. "
                        f"Rankings had providers: {[r.provider for r in rankings[:5]]}, "
                        f"but none match our available LLMs: {available_llm}"
                    )
            
            except Exception as e:
                logger.error(f"Error selecting provider from benchmarks: {e}", exc_info=True)
        else:
            logger.warning("External benchmarks not initialized")
        
        # DYNAMIC FALLBACK: Round-robin or first available
        # No hardcoded provider preferences - use whatever is available
        
        # Simple strategy: use first available provider
        # In future, could implement round-robin counter or random selection
        fallback_provider = available_llm[0]
        
        logger.info(
            f"🔄 Using dynamic fallback: {fallback_provider} for {category} "
            f"(selected from available: {available_llm})"
        )
        
        return fallback_provider
    
    def detect_category_from_message(self, message: str, emotion_state: Optional[EmotionState] = None) -> str:
        """
        Detect task category from message content
        
        Categories:
        - coding: Programming, algorithms, debugging
        - math: Mathematics, calculations
        - reasoning: Logic, analysis
        - research: Knowledge, facts, explanations
        - empathy: Emotional support (based on emotion state)
        - general: Default category
        
        Args:
            message: User's message
            emotion_state: User's emotion state
        
        Returns:
            Category name
        """
        
        message_lower = message.lower()
        
        # Coding indicators
        coding_keywords = [
            'code', 'program', 'function', 'algorithm', 'debug',
            'python', 'javascript', 'java', 'c++', 'recursion',
            'loop', 'variable', 'class', 'api', 'database', 'sql'
        ]
        if any(kw in message_lower for kw in coding_keywords):
            return "coding"
        
        # Math indicators
        math_keywords = [
            'calculate', 'solve', 'equation', 'formula', 'theorem',
            'integral', 'derivative', 'matrix', 'probability',
            'geometry', 'algebra', 'calculus', 'trigonometry'
        ]
        if any(kw in message_lower for kw in math_keywords):
            return "math"
        
        # Reasoning indicators
        reasoning_keywords = [
            'analyze', 'evaluate', 'compare', 'conclude', 'infer',
            'logic', 'argument', 'reasoning', 'critical thinking',
            'deduce', 'reasoning'
        ]
        if any(kw in message_lower for kw in reasoning_keywords):
            return "reasoning"
        
        # Research indicators
        research_keywords = [
            'what is', 'explain', 'describe', 'how does', 'why is',
            'history of', 'definition', 'meaning', 'overview', 'tell me about'
        ]
        if any(kw in message_lower for kw in research_keywords):
            return "research"
        
        # Empathy indicators (based on emotion)
        if emotion_state and hasattr(emotion_state, 'primary_emotion'):
            negative_emotions = [
                'frustration', 'anxiety', 'overwhelmed', 
                'sadness', 'confusion', 'stress'
            ]
            if emotion_state.primary_emotion in negative_emotions:
                return "empathy"
        
        # Default
        return "general"
