import time

from typing import Optional
from openai import ChatCompletion, util
from openai.error import TryAgain

from src.openai_python_cache.provider import Sqlite3CacheProvider


class ChatCompletion(ChatCompletion):
    def __init__(self):
        pass

    @classmethod
    def create(
        cls,
        cache_provider: Optional[Sqlite3CacheProvider] = None,
        *args,
        **kwargs,
    ):
        """
        @overrides openai/api_resources/chat_completion.py#L13
        81e624e8ba3b0d36e0c14a437c7ff4171d35b5c0

        Creates a new chat completion for the provided messages and parameters.
        See https://platform.openai.com/docs/api-reference/chat-completions/create
        for a list of valid parameters.
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        params = kwargs

        if cache_provider is not None:
            cache_key = cache_provider.hash_params(params)
            cached_response = cache_provider.get(cache_key)
            if cached_response:
                # Cache hit, return the cached response
                return cached_response

            # Cache miss, make the request and cache it
            while True:
                try:
                    response = super().create(*args, **kwargs)
                    cache_provider.insert(cache_key, params, response)
                    return response
                except TryAgain as e:
                    if timeout is not None and time.time() > start + timeout:
                        raise

                    util.log_info("Waiting for model to warm up", error=e)
