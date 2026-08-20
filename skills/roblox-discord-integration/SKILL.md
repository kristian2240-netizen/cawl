# Roblox ↔ Discord Integration APIs

## Purpose
Look up linked Roblox-Discord accounts across verification services. Zero-cookie, mostly free.

## Tier 0: No Auth, No Key

### verify.eryn.io (RoVer Public API)
Free, no key, no signup. The original Roblox-Discord verification service used by the official Roblox Discord.

```
GET https://verify.eryn.io/api/user/{discord_id}
```

**Response:**
```json
{
  "status": "ok",
  "robloxId": 12345678,
  "robloxUsername": "SomeUser",
  "verified": true
}
```

- No auth required
- No documented rate limit
- Works for any user verified through RoVer or the Roblox Discord server
- Returns 404 if user not verified
- **Note:** May return 403 from some networks/regions (Cloudflare protection). Try from different network if blocked.

### disdex.io (Cross-Platform Search)
Free, no key. Search servers that use Roblox-Discord verification.

```
GET https://disdex.io/api/v1/servers?q={roblox_game_name}&sort=members
```

Useful for finding communities that link Roblox + Discord.

## Tier 1: Free With Key (Sign Up Required)

### Bloxlink API
Free tier. Sign up at https://blox.link/dashboard/user/developer

**Base URL:** `https://api.blox.link/v4/`

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/public/guilds/{guild_id}/discord-to-roblox/{discord_id}` | GET | Guild API Key | Discord → Roblox (server members only) |
| `/public/discord-to-roblox/{discord_id}` | GET | Global API Key | Discord → Roblox (any user) |
| `/public/guilds/{guild_id}/roblox-to-discord/{roblox_id}` | GET | Guild API Key | Roblox → Discord (server members only) |
| `/public/roblox-to-discord/{roblox_id}` | GET | Global API Key | Roblox → Discord (any user) |

**Response:**
```json
{
  "robloxId": "12345678",
  "roblox": {
    "username": "SomeUser",
    "displayName": "Some User",
    "avatar": "https://..."
  }
}
```

**Notes:**
- Guild API key = scoped to one Discord server
- Global API key = works across all Bloxlink-verified users
- Free tier has generous limits
- Reverse lookups (Roblox → Discord) limited on free tier

### RoVer Registry API
Free tier. Sign up at https://rover.link → Bot Developer API

**Base URL:** `https://registry.rover.link/api`

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/guilds/{guild_id}/discord-to-roblox/{discord_id}` | GET | Bearer token | Discord → Roblox (server member) |
| `/guilds/{guild_id}/roblox-to-discord/{roblox_id}` | GET | Bearer token | Roblox → Discord (server member) |
| `/discord-to-roblox/{discord_id}` | GET | Bearer token | Discord → Roblox (global) |
| `/roblox-to-discord/{roblox_id}` | GET | Bearer token | Roblox → Discord (global) |

**Response:**
```json
{
  "discordId": "123456789012345678",
  "robloxId": "12345678",
  "robloxUsername": "SomeUser",
  "verified": true
}
```

**Auth header:** `Authorization: Bearer {api_key}`

### RoWifi API
Free tier. Another popular verification service.

**Base URL:** `https://rowifi.link/api/v1`

| Endpoint | Method | Description |
|---|---|---|
| `/guilds/{guild_id}/users/{discord_id}` | GET | Discord → Roblox (server member) |
| `/guilds/{guild_id}/roblox-to-discord/{roblox_id}` | GET | Roblox → Discord (server member) |

**Auth:** API key required (get from RoWifi dashboard)

### VerifyUGC API
Free tier: 100 calls/day. Cross-platform blacklist + trust scores.

**Base URL:** `https://verifyugc.dev/v1`

| Endpoint | Method | Description |
|---|---|---|
| `/blacklist/check?provider=roblox&id={user_id}` | GET | Check if Roblox account is blacklisted |
| `/blacklist/check?provider=discord&id={user_id}` | GET | Check if Discord account is blacklisted |
| `/users/{handle}` | GET | Creator profile + trust score |

**Auth:** `Authorization: Bearer {api_key}` (free tier key from dashboard)

## Tier 2: Library Wrappers

### RBLXVerify (npm)
Unified wrapper for Bloxlink, RoVer, RoWifi, and RBXBolt.

```js
const rblxverify = require('rblxverify');

// Discord → Roblox
await rblxverify.bloxlink('discord_id');        // Bloxlink
await rblxverify.rover('discord_id');           // RoVer
await rblxverify.rowifi('discord_id');          // RoWifi
await rblxverify.rbxbolt('discord_id', 'key');  // RBXBolt
```

### pybloxlink (Python)
Async wrapper for Bloxlink API.

```python
from pybloxlink import Bloxlink

bloxlink = Bloxlink(api_key="YOUR_KEY")
roblox_id = await bloxlink.lookup_roblox_user(discord_id)
discord_id = await bloxlink.lookup_discord_user(roblox_id)
```

## Usage Patterns

### Quick Discord → Roblox (No Auth)
```
1. Try verify.eryn.io/api/user/{discord_id}
   - If "ok" → you have robloxId + robloxUsername
   - If 404 → user not verified through RoVer
2. Use Roblox API: users.rotunnel.com/v1/users/{robloxId}
   - Get full profile, avatar, groups
```

### Quick Roblox → Discord (No Auth)
```
1. verify.eryn.io doesn't support reverse lookup
2. Use disdex.io to find servers the user might be in
3. Or use Bloxlink/RoVer with a free API key
```

### Full Investigation Flow
```
1. verify.eryn.io → get robloxId from discord_id (no auth)
2. users.rotunnel.com → get Roblox profile from robloxId (no auth)
3. groups.rotunnel.com → get user's groups (no auth)
4. discord.dog → get Discord profile from discord_id (no auth)
5. disdex.io → find mutual servers (no auth)
```

### Bulk Verification Check
```
1. For each discord_id:
   - GET verify.eryn.io/api/user/{discord_id}
   - If verified: log robloxId
   - If not: mark as unverified
2. For verified robloxIds:
   - GET users.rotunnel.com/v1/users/{robloxId}
   - Log username, avatar, groups
```

## Rate Limits Summary

| Service | Auth | Rate Limit | Daily Limit |
|---|---|---|---|
| verify.eryn.io | None | Undocumented (be reasonable) | Unlimited |
| disdex.io | None | None | Unlimited |
| Bloxlink (free) | API key | Generous | High |
| RoVer (free) | Bearer token | Standard Discord API limits | High |
| RoWifi (free) | API key | Standard | High |
| VerifyUGC (free) | Bearer token | Standard | 100/day |

## Error Handling
- `404` on verify.eryn.io → User not verified through RoVer
- `404` on Bloxlink → User not linked or not in guild
- `401` → Invalid/expired API key
- `429` → Rate limited, check Retry-After header
- `403` → Insufficient permissions or wrong key type

## Anti-Patterns
- Don't use .ROBLOSECURITY cookie for verification lookups
- Don't store API keys in code — use environment variables
- Don't abuse free tiers — these services run on goodwill
- Don't assume all users are verified — many aren't
- verify.eryn.io only works for RoVer/Roblox Discord verified users
- Reverse lookups (Roblox → Discord) are more restricted across all services
