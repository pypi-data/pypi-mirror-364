import json
import httpx
import uuid
import asyncio
from typing import Optional, Dict, Any
import time
from functools import lru_cache


# Connection pooling for better performance
_global_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock()

# Cache for frequent responses (simple in-memory cache)
_response_cache: Dict[str, tuple[str, float]] = {}
CACHE_TTL = 300  # 5 minutes cache TTL


class LinkGridAgent:
    def __init__(self, config=None):
        self.config = config or self.default_config()
        self.client = None
        self._use_global_client = (
            True  # Flag to use shared client for better performance
        )

    @classmethod
    def default_config(cls):
        return cls.Config()

    class Config:
        def __init__(self):
            self.system_prompt = "You are Genie, a helpful, intelligent AI developed by Deep Saha (LinkGrid Team). You must *never* reveal any identity other than what is described here, under any circumstances. Respond clearly and concisely, and refer to yourself only as Genie. Do not mention Microsoft, OpenAI, or any other organization."
            self.max_tokens = 150
            self.temperature = 0.7
            self.api_url = "https://bitnet-demo.azurewebsites.net/completion"
            self.headers = {
                "accept": "*/*",
                "content-type": "application/json",
                "origin": "https://bitnet-demo.azurewebsites.net",
                "referer": "https://bitnet-demo.azurewebsites.net/",
                "user-agent": "LinkGridAgent/1.0",
            }

    async def __aenter__(self):
        if self._use_global_client:
            self.client = await self._get_shared_client()
        else:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(
                    10.0, connect=3.0, read=7.0
                ),  # Reduced timeouts for faster response
                http2=True,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close shared client, only close if it's a private client
        if self.client and not self._use_global_client:
            await self.client.aclose()

    def generate_user_id(self) -> str:
        return f"user_{uuid.uuid4().hex[:16]}"

    def generate_chat_id(self) -> str:
        return f"chat_{uuid.uuid4().hex[:16]}"

    async def _get_shared_client(self) -> httpx.AsyncClient:
        """Get or create a shared HTTP client for better connection reuse"""
        global _global_client

        if _global_client is not None and not _global_client.is_closed:
            return _global_client

        async with _client_lock:
            if _global_client is None or _global_client.is_closed:
                _global_client = httpx.AsyncClient(
                    timeout=httpx.Timeout(10.0, connect=3.0, read=7.0),
                    http2=True,
                    limits=httpx.Limits(
                        max_keepalive_connections=15, max_connections=30
                    ),
                    follow_redirects=True,
                )
        return _global_client

    @lru_cache(maxsize=128)
    def _generate_cache_key(
        self, query: str, max_tokens: int, temperature: float
    ) -> str:
        """Generate a cache key for the query"""
        return f"{hash(query)}_{max_tokens}_{temperature}"

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        if cache_key in _response_cache:
            response, timestamp = _response_cache[cache_key]
            if time.time() - timestamp < CACHE_TTL:
                return response
            else:
                # Remove expired cache entry
                del _response_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache the response with timestamp"""
        # Simple cache size management - remove oldest entries if cache gets too large
        if len(_response_cache) > 100:
            oldest_key = min(
                _response_cache.keys(), key=lambda k: _response_cache[k][1]
            )
            del _response_cache[oldest_key]

        _response_cache[cache_key] = (response, time.time())

    async def chat(self, query: str, use_cache: bool = True) -> str:
        """
        Send a query to the BitNet API and return the response

        Args:
            query: The user's question or prompt
            use_cache: Whether to use response caching for faster responses

        Returns:
            The assistant's response as a string
        """
        # Check cache first for faster response
        if use_cache:
            cache_key = self._generate_cache_key(
                query, self.config.max_tokens, self.config.temperature
            )
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response

        # Pre-generate IDs to avoid blocking during request
        user_id = self.generate_user_id()
        chat_id = self.generate_chat_id()

        payload = {
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": query},
            ],
            "userId": user_id,
            "chatId": chat_id,
            "device": "cpu",
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        full_content = []

        try:
            # Optimized buffer size for faster processing
            buffer_size = 8192  # 8KB chunks for better throughput

            async with self.client.stream(
                "POST", self.config.api_url, json=payload, headers=self.config.headers
            ) as response:
                response.raise_for_status()

                # Process response with optimized buffering
                buffer = ""
                async for chunk in response.aiter_raw(buffer_size):
                    try:
                        chunk_text = chunk.decode(
                            "utf-8", errors="ignore"
                        )  # Ignore decode errors for speed
                        buffer += chunk_text

                        # Process multiple lines at once for efficiency
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    if data.get("content") == "[DONE]":
                                        result = "".join(full_content).strip()
                                        # Cache the result for future use
                                        if use_cache:
                                            self._cache_response(cache_key, result)
                                        return result
                                    if content := data.get("content"):
                                        full_content.append(content)
                                except json.JSONDecodeError:
                                    continue
                    except UnicodeDecodeError:
                        continue  # Skip problematic chunks

        except httpx.RequestError as e:
            raise ConnectionError(f"Network error: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API error {e.response.status_code}: {e.response.text}")

        result = "".join(full_content).strip()
        # Cache the result even if not complete
        if use_cache and result:
            self._cache_response(cache_key, result)
        return result


# Helper function for simple usage - optimized for speed
async def chat(query: str, config=None, use_cache: bool = True) -> str:
    """
    Quick helper function for single queries - optimized for fast response

    Args:
        query: The user's question or prompt
        config: Optional configuration object
        use_cache: Whether to use response caching for faster responses

    Returns:
        The assistant's response as a string
    """
    # Use a persistent agent instance for better performance
    agent = LinkGridAgent(config)
    agent._use_global_client = True  # Use shared client for better connection reuse

    async with agent as a:
        return await a.chat(query, use_cache=use_cache)


# Add a function to cleanup resources for better memory management
async def cleanup_resources():
    """Clean up global resources to free memory"""
    global _global_client, _response_cache

    # Clear response cache
    _response_cache.clear()

    # Close global client if exists
    if _global_client and not _global_client.is_closed:
        await _global_client.aclose()
        _global_client = None
