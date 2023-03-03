# 🍰 openai-python-cache

A thin wrapper around the OpenAI Python bindings for caching responses.

## Motivation

I'm experimenting with a large-ish dataset locally that gets injected into GPT
prompts. Responses are not perfect, and occassionally I have to tweak some
of my data. This means that I'm making API calls for results that are okay,
because it's iterating over the entire dataset.

This solves the issue by cache-ing OpenAI responses in a local SQLite3 database.
**Only ChatCompletion is supported** at this time because it's the only API I use.

This is a quick and dirty solution. I'd go a level lower and inject this
behaviour directly in the requestor, but I don't have time to figure that
part out (yet?)!

## Installation

```sh
# Using pip:
$ pip install openai-python-cache

# Using poetry:
$ poetry add openai-python-cache
```

## Usage

```python
import os
import openai
from openai_python_cache.api import ChatCompletion
from openai_python_cache.provider import Sqlite3CacheProvider

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Create a cache provider
cache_provider = Sqlite3CacheProvider()

# Use the ChatCompletion class from `openai_python_cache`
completion = ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "Tell the world about the ChatGPT API in the style of a pirate.",
        }
    ],
    # Inject the cache provider. Requests will NOT be cached if this is not
    # provided!
    cache_provider=cache_provider,
)

print(completion)
```

## Demo

```python
import os
import time
import openai
from openai_python_cache.api import ChatCompletion
from openai_python_cache.provider import Sqlite3CacheProvider

openai.api_key = os.environ.get("OPENAI_API_KEY")

cache_provider = Sqlite3CacheProvider()

params = {
    'model': "gpt-3.5-turbo",
    'messages': [
        {
            "role": "user",
            "content": "Testing cache!",
        }
    ]
}

# First request, cache miss. This will result in an API call to OpenAI, and
# the response will be saved to cache.
c0start = time.time()
ChatCompletion.create(cache_provider, **params)
c0end = time.time() - c0start
print(f"First request is a cache miss. It took {c0end} seconds!")
# >>> First request is a cache miss. It took 1.7009928226470947 seconds!

# Second request, cache hit. This will NOT result in an API call to OpenAI.
# The response will be served from cache.
c1start = time.time()
ChatCompletion.create(cache_provider, **params)
c1end = time.time() - c1start
print(f"Second request is a cache hit. It took {c1end} seconds!")
# >>> Second request is a cache hit. It took 0.00015616416931152344 seconds!
```
