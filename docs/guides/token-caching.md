# Token Caching

restful automatically caches bearer tokens to avoid re-authenticating on every request.

## How It Works

1. First request triggers a POST to the `login_path` configured for the API
2. The response token is parsed for its JWT `exp` claim
3. Token and expiry are cached to `.restful/cache.json`, keyed by base URL
4. Subsequent requests use the cached token
5. When the token is within 60 seconds of expiry, it's automatically refreshed
6. On 401 response, the token is invalidated and a fresh login is performed

## Cache File

```json
{
  "https://100.94.115.90": {
    "token": "eyJhbG...",
    "expires_at": 1711500000
  },
  "https://api.example.com": {
    "token": "eyJhbG...",
    "expires_at": 1711600000
  }
}
```

## Security

- File permissions are set to 0600 (owner-only read/write)
- Writes are atomic (temp file + rename) to prevent corruption
- Tokens are never logged or printed
- The cache file is in `.restful/` which is gitignored by default

## Multiple APIs

Each API's base URL gets its own cache entry. Switching between APIs or VMs doesn't invalidate other cached tokens.

## Manual Invalidation

Deleting `.restful/cache.json` forces a fresh login on the next request.
