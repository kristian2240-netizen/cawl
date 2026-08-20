# Roblox Investigation API Tools

## Purpose
Investigate Roblox users, games, groups, catalog items, and servers using public API endpoints. No cookies or authentication required.

## Proxy
All requests go through RoTunnel (free, no signup, no rate limits):
- Replace `roblox` → `rotunnel` in any Roblox API domain
- Example: `games.roblox.com` → `games.rotunnel.com`

## Endpoints (No Auth Required)

### Users
| Endpoint | Method | Description |
|---|---|---|
| `users.rotunnel.com/v1/users/{userId}` | GET | User profile (name, display, description, created, banned) |
| `users.rotunnel.com/v1/users` | POST | Batch user lookup (body: `{"userIds": [1,2,3]}`, max 100) |
| `users.rotunnel.com/v1/users/search?keyword={name}&limit={n}` | GET | Search users by name |
| `users.rotunnel.com/v1/users/{userId}/username-history?limit={n}` | GET | Past usernames |
| `users.rotunnel.com/v1/users/{userId}/avatar` | GET | User avatar URLs |
| `users.rotunnel.com/v1/users/{userId}/avatar/headshot` | GET | Headshot URLs |
| `presence.rotunnel.com/v1/presence/users` | POST | Online status (body: `{"userIds": [1,2]}`) |

### Games
| Endpoint | Method | Description |
|---|---|---|
| `games.rotunnel.com/v1/games?universeIds={id}` | GET | Game info (name, description, playing, visits, votes) |
| `games.rotunnel.com/v1/games/{universeId}/servers/{serverType}?limit={n}` | GET | Server list (serverType: `All`, `Public`, `Friends`, `Private`) |
| `games.rotunnel.com/v1/games/list?keyword={query}&limit={n}` | GET | Search games |
| `games.rotunnel.com/v1/games/{universeId}/favorites/count` | GET | Favorite count |
| `games.rotunnel.com/v1/games/multiget?universeIds={ids}` | GET | Batch game lookup (max 50) |
| `games.rotunnel.com/v1/games/{universeId}/votes` | GET | Up/down vote breakdown |
| `develop.rotunnel.com/v1/universes/{universeId}` | GET | Universe/developer metadata |
| `develop.rotunnel.com/v1/universes/{universeId}/places` | GET | Places in a universe |

### Groups
| Endpoint | Method | Description |
|---|---|---|
| `groups.rotunnel.com/v1/groups/{groupId}` | GET | Group info (name, description, memberCount, owner) |
| `groups.rotunnel.com/v1/groups/{groupId}/roles` | GET | Group roles |
| `groups.rotunnel.com/v1/groups/{groupId}/users?limit={n}&sortOrder={Asc\|Desc}` | GET | Group members |
| `groups.rotunnel.com/v1/users/{userId}/groups/roles` | GET | User's groups |

### Catalog / Marketplace
| Endpoint | Method | Description |
|---|---|---|
| `catalog.rotunnel.com/v1/search/items?category={cat}&keyword={q}&limit={n}` | GET | Search catalog items |
| `catalog.rotunnel.com/v1/items/{itemId}/details` | GET | Item details |
| `catalog.rotunnel.com/v1/items/{itemId}/recommendations` | GET | Similar items |

### Badges
| Endpoint | Method | Description |
|---|---|---|
| `badges.rotunnel.com/v1/universes/{universeId}/badges?limit={n}` | GET | Game badges |
| `badges.rotunnel.com/v1/badges/{badgeId}` | GET | Badge details |

### Thumbnails
| Endpoint | Method | Description |
|---|---|---|
| `thumbnails.rotunnel.com/v1/games/icons?universeIds={ids}&size={size}&format=Png` | GET | Game icons |
| `thumbnails.rotunnel.com/v1/users/avatar-headshot?userIds={ids}&size={size}&format=Png` | GET | User headshots |
| `thumbnails.rotunnel.com/v1/users/avatar-bust?userIds={ids}&size={size}&format=Png` | GET | User busts |

### Search
| Endpoint | Method | Description |
|---|---|---|
| `search.rotunnel.com/v2/search-suggestions?keyword={q}` | GET | Autocomplete suggestions |
| `search.rotunnel.com/v2/search?keyword={q}&pageType=1` | GET | Global search (1=Games, 2=Players, 3=Catalog, 11=Groups) |

## Usage Patterns

### User Investigation
```
1. Search user: GET users.rotunnel.com/v1/users/search?keyword={name}&limit=5
2. Get profile: GET users.rotunnel.com/v1/users/{userId}
3. Get avatar: GET users.rotunnel.com/v1/users/{userId}/avatar
4. Get groups: GET groups.rotunnel.com/v1/users/{userId}/groups/roles
5. Check online: POST presence.rotunnel.com/v1/presence/users (body: {"userIds": [userId]})
6. Username history: GET users.rotunnel.com/v1/users/{userId}/username-history
```

### Game Investigation
```
1. Search game: GET games.rotunnel.com/v1/games/list?keyword={name}&limit=10
2. Get details: GET games.rotunnel.com/v1/games?universeIds={universeId}
3. Get votes: GET games.rotunnel.com/v1/games/{universeId}/votes
4. Get servers: GET games.rotunnel.com/v1/games/{universeId}/servers/Public?limit=10
5. Get badges: GET badges.rotunnel.com/v1/universes/{universeId}/badges
6. Get places: GET develop.rotunnel.com/v1/universes/{universeId}/places
```

### Catalog Investigation
```
1. Search items: GET catalog.rotunnel.com/v1/search/items?category=All&keyword={query}&limit=30
2. Get details: GET catalog.rotunnel.com/v1/items/{itemId}/details
3. Get recommendations: GET catalog.rotunnel.com/v1/items/{itemId}/recommendations
```

### Group Investigation
```
1. Get group: GET groups.rotunnel.com/v1/groups/{groupId}
2. Get roles: GET groups.rotunnel.com/v1/groups/{groupId}/roles
3. Get members: GET groups.rotunnel.com/v1/groups/{groupId}/users?limit=100
4. Check user's groups: GET groups.rotunnel.com/v1/users/{userId}/groups/roles
```

## Category IDs (Catalog)
| ID | Category |
|---|---|
| 1 | All |
| 2 | Hats |
| 3 | Shirts |
| 4 | T-Shirts |
| 5 | Pants |
| 6 | Heads |
| 7 | Faces |
| 8 | Gear |
| 9 | Accessories |
| 10 | Audio |
| 11 | Animations |
| 12 | Animation Packs |
| 13 | Body Parts |
| 14 | Environmental |
| 15 | Poses |
| 16 | Model Packs |
| 17 | Plugins |
| 19 | Decals |
| 21 | Video |

## Page Types (Search)
| ID | Type |
|---|---|
| 1 | Games |
| 2 | Players |
| 3 | Catalog Items |
| 11 | Groups |

## Error Handling
- `429` Too Many Requests → Retry with exponential backoff
- `404` Not Found → Entity doesn't exist, check ID
- `400` Bad Request → Check parameters
- RoTunnel mirrors Roblox responses exactly

## Anti-Patterns
- Don't use `.ROBLOSECURITY` cookie for read-only investigation (unnecessary risk)
- Don't spam presence checks (rate-limited at Roblox side)
- Don't cache user data for more than 5 minutes (profiles change)
- Always use RoTunnel proxy, not direct Roblox endpoints (avoids CORS/rate limits)
