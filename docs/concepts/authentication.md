# Authentication

restful supports two authentication strategies, configured per-API in the workspace config.

## Bearer Token Auth

Automatic JWT lifecycle: login, cache, refresh, retry.

```yaml
auth:
  type: bearer
  login_path: /security/v1/auth/login
  username: admin
  password_env: SFM_PASSWORD
```

**How it works:**

1. On first request, POST to `login_path` with username/password
2. Extract token from response, parse JWT `exp` claim
3. Cache to `.restful/cache.json` keyed by base URL
4. Inject `Authorization: Bearer <token>` on every request
5. If token expires within 60s, auto-refresh before the next request
6. On 401 response: invalidate token, re-authenticate, retry once

**Password handling:** The `password_env` field names an environment variable — passwords are never stored in config files.

## API Key Auth

Static key injected as a header:

```yaml
auth:
  type: apikey
  header: Authorization
  key_env: NETBOX_API_KEY
```

The value of the environment variable named by `key_env` is sent as the specified header on every request.

## No Auth

```yaml
auth:
  type: none
```

Or omit the `auth` section entirely.

## Token Cache

Cached tokens are stored in `.restful/cache.json`:

```json
{
  "https://100.94.115.90": {
    "token": "eyJhbG...",
    "expires_at": 1711500000
  }
}
```

- Keyed by base URL — multiple APIs each get their own entry
- File permissions are 0600 (owner-only)
- Atomic writes using temp file + rename
- Never logged or printed
