# Discord Investigation API Tools

## Purpose
Investigate Discord users, servers, invites, and bots. Multiple tiers — from zero-auth public lookups to bot-token endpoints.

## Tier 0: No Auth, No Rate Limit (Use First)

### Snowflake Decoder (Timestamp from ID)
Discord IDs are snowflakes — creation timestamp is encoded IN the ID. No API call needed.

```
timestamp_ms = (id >> 22) + 1420070400000
```

**Pseudocode:**
```
snowflake_to_timestamp(snowflake):
    return ((snowflake >> 22) + 1420070400000)
```

### Discord CDN (Public Assets)
No auth. Construct URLs from user/avatar hashes.

| Asset | URL Pattern |
|---|---|
| Avatar | `https://cdn.discordapp.com/avatars/{user_id}/{hash}.png?size=512` |
| Avatar (animated) | `https://cdn.discordapp.com/avatars/{user_id}/{hash}.gif?size=512` |
| Banner | `https://cdn.discordapp.com/banners/{user_id}/{hash}.png?size=600` |
| Guild Icon | `https://cdn.discordapp.com/icons/{guild_id}/{hash}.png?size=512` |
| Guild Banner | `https://cdn.discordapp.com/banners/{guild_id}/{hash}.png?size=600` |
| Default Avatar | `https://cdn.discordapp.com/embed/avatars/{discriminator % 5}.png` |

**Default avatar by ID (new username system):**
```
https://cdn.discordapp.com/embed/avatars/{(user_id >> 22) % 6}.png
```

## Tier 1: Free Third-Party APIs (No Key, No Auth)

### DiscordLookup (mesalytic.moe)
Free, no key, no signup. Best for user profiles.

```
GET https://discordlookup.mesalytic.moe/v1/user/{user_id}
```

Returns: username, global_name, avatar, banner, accent_color, public_flags, locale, created_at, clan (if any), connections.

### disdex.io API
Free, no key, no signup. Best for server/user/invite search. **Tested working.**

**Base URL:** `https://disdex.io/api/v1`

| Endpoint | Method | Description |
|---|---|---|
| `/servers?q={query}&limit={n}` | GET | Search servers (min 3 chars). Returns `{data: [...]}` |
| `/users?q={query}&type={user\|bot}&limit={n}` | GET | Search users/bots by username prefix (min 3 chars) |
| `/invites/{code}` | GET | Resolve invite to server (even dead invites). Returns `{status: "live"\|"dead"\|"pending"\|"unknown", server: {...}}` |

**Query params for /servers:**
- `q` — search term (3+ chars)
- `lang` — ISO 639-1 code (en, es, de)
- `tag` — guild tag (exact match)
- `sort` — members, online, boosts, newest, oldest
- `nsfw` — include, exclude, only
- `vanity` — any, has, no, only
- `limit`, `offset` — pagination

**Query params for /users:**
- `q` — username prefix (3+ chars)
- `type` — user or bot
- `sort` — invites, servers, username, newest, oldest

**Response format:** `{data: [...], total: null, limit: n, offset: 0, has_more: bool}`

### discord.dog API
Free, no key. Good user lookup with presence data. **Tested working.**

**Base URL:** `https://discord.dog/api`

| Endpoint | Method | Description |
|---|---|---|
| `/users/{user_id}` | GET | User profile with presence (online status, activities, Spotify, games) |
| `/{user_id}` | GET (web) | Full profile page (avatar, bio, badges, connections, live status) |

**Response fields:** id, username, globalName, discriminator, avatarHash, bannerHash, accentColor, publicFlags, bot, presence (status, clientStatus, activities[])

### Lanyard API (Live Presence)
Free. Requires user to join discord.gg/lanyard (130K+ members). May have TLS issues from some networks.

```
GET https://api.lanyard.xyz/v1/user/{user_id}
```

Returns: online status, activities (Spotify, games, custom status), devices, discord_user, discord_presence.

## Tier 2: Discord API (Bot Token Required)

Bot token needed but still useful to document.

**Base URL:** `https://discord.com/api/v10`

### Users
| Endpoint | Method | Description |
|---|---|---|
| `/users/{user_id}` | GET | User profile (username, avatar, banner, flags, bot status) |
| `/users/@me` | GET | Current user (requires auth) |

### Guilds
| Endpoint | Method | Description |
|---|---|---|
| `/guilds/{guild_id}?with_counts=true` | GET | Guild info (name, icon, description, member/online counts, boost level) |
| `/guilds/{guild_id}/preview` | GET | Guild preview (works for discoverable guilds) |

### Invites
| Endpoint | Method | Description |
|---|---|---|
| `/invites/{code}?with_counts=true` | GET | Invite details (guild, channel, inviter, member counts) |
| `/guilds/{guild_id}/invites` | GET | List guild invites (requires permissions) |

### Channels
| Endpoint | Method | Description |
|---|---|---|
| `/channels/{channel_id}` | GET | Channel info |
| `/channels/{channel_id}/messages?limit={n}` | GET | Recent messages (requires permissions) |

### Application/Bot
| Endpoint | Method | Description |
|---|---|---|
| `/oauth2/applications/@me` | GET | Current bot application info |

## Usage Patterns

### User Investigation (No Auth)
```
1. Decode snowflake: (id >> 22) + 1420070400000 = creation timestamp
2. Full profile: GET discordlookup.mesalytic.moe/v1/user/{user_id}
3. Avatar URL: https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png
4. Banner URL: https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.png
5. Live presence: GET lanyard.kwiatekmiki.com/api/v1/user/{user_id} (if joined Lanyard)
6. Check if bot: public_flags & (1 << 18) in DiscordLookup response
```

### Server Investigation (No Auth)
```
1. Search servers: GET disdex.io/api/v1/servers?q={name}&sort=members
2. Check invite: GET disdex.io/api/v1/invites/{code} (even dead invites)
3. Get server details: (need bot token or use DiscordLookup for guilds with counts)
```

### Invite Investigation (No Auth)
```
1. Resolve invite: GET disdex.io/api/v1/invites/{code}
   - Returns: server name, member count, online count, status (live/dead/pending)
2. If dead, disdex may have cached the server info
3. Check other invites for same server in response
```

### Bot Investigation (No Auth)
```
1. Check public_flags bit 18 (IS_BOT)
2. Search bots: GET disdex.io/api/v1/users?q={name}&type=bot
3. Bot application info requires token: GET /oauth2/applications/@me
```

## Discord Badges (public_flags bitmask)

| Bit | Badge |
|---|---|
| 1 << 0 | Staff |
| 1 << 1 | Partner |
| 1 << 2 | Hypesquad Events |
| 1 << 3 | Bug Hunter Level 1 |
| 1 << 4 | Bug Hunter Level 2 |
| 1 << 5 | Hypesquad Bravery |
| 1 << 6 | Hypesquad Brilliance |
| 1 << 7 | Hypesquad Balance |
| 1 << 8 | Early Supporter |
| 1 << 9 | Team User |
| 1 << 10 | System |
| 1 << 11 | Bug Hunter Level 3 |
| 1 << 12 | Verified Bot Developer |
| 1 << 14 | Certified Moderator |
| 1 << 16 | Bot HTTP Interactions |
| 1 << 18 | Bot (IS_BOT) |
| 1 << 20 | Active Developer |

## Error Handling
- `429` Rate Limited → Check Retry-After header, backoff exponentially
- `404` Not Found → User/guild doesn't exist or deleted
- `403` Forbidden → Bot lacks permissions or endpoint requires auth
- `10013` Unknown User → Invalid user ID
- `10004` Unknown Guild → Bot not in guild (for guild endpoints)

## Anti-Patterns
- Don't use `.ROBLOSECURITY` or Discord tokens for read-only lookups
- Don't cache user data for more than 5 minutes
- Don't abuse DiscordLookup — they run a free service
- Don't share bot tokens in code or logs
- Snowflake timestamps are UTC
- Avatar hashes starting with `a_` are animated (use .gif)
