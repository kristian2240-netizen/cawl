# WorldWideView Integration Skill

## Purpose
Connect C.A.W.L. to WorldWideView — a 3D geospatial intelligence globe. Query live data on flights, maritime, earthquakes, weather, ISS, conflicts, traffic cameras, and any installed plugin. Control the globe camera, toggle layers, investigate areas.

## Prerequisites
- WorldWideView must be running: `cd C:\Users\Kristian\worldwideview && pnpm dev:all`
- Generate an API key at `http://localhost:3000/setup` → Settings → API Keys
- Set `WWV_API_KEY` in CAWL config (via CONFIG page or `.cawl-data/settings.json`)

## Architecture
```
CAWL (port 8123) → WWV MCP endpoint (port 3000/api/mcp) → WWV Data Engine (port 5000)
```

## How to Use

### Status Check
```python
from src.test_project import worldwideview as wwv
wwv.status()  # Returns connection status, tool count, health
```

### Search Entities
```python
wwv.search_entities("flights near London", plugin_id="aviation", limit=10)
wwv.search_entities("earthquakes today")
wwv.search_entities("ISS position")
```

### Investigate an Area
```python
wwv.investigate_area("Tokyo", entity_type="flights", radius_km=200)
wwv.investigate_area("Mediterranean Sea", entity_type="maritime")
```

### Geocode a Location
```python
wwv.geocode_location("Buckingham Palace")
# Returns lat/lon coordinates
```

### Globe Camera Control
```python
wwv.fly_to(lat=51.5074, lon=-0.1278, altitude=500000)  # Fly to London
wwv.toggle_layer("aviation", visible=True)               # Show flights
wwv.toggle_layer("earthquakes", visible=False)           # Hide earthquakes
```

### Entity Details
```python
wwv.get_entity_details("entity-id-here")
wwv.get_plugin_data("aviation")  # Full snapshot from a plugin
```

### List Available Plugins
```python
wwv.list_plugins()  # Shows all installed data layers
```

### Region Queries (Bounding Box)
```python
wwv.get_entities_in_region(north=52.0, south=51.0, east=0.5, west=-0.5, plugin_id="aviation")
```

### Globe Context
```python
wwv.get_globe_context()  # What's currently visible on the globe
```

### Direct REST (bypassing MCP)
```python
wwv.rest_search("aircraft", plugin_id="aviation")
wwv.rest_region(north=52, south=51, east=0.5, west=-0.5)
wwv.engine_snapshot("aviation")  # Raw Data Engine data
wwv.engine_manifest()            # List of active engine plugins
```

### Health Check
```python
wwv.health_check()  # Check if WWV is running
wwv.status()        # Full status: health, tools, resources, config
```

## Available MCP Tools (25+)
| Category | Tools |
|----------|-------|
| Globe | `pan_globe`, `focus_entity`, `toggle_layer`, `set_timeline` |
| Data | `search_entities`, `get_entities_in_region`, `get_entity_details`, `get_plugin_data` |
| Discovery | `list_available_plugins`, `get_globe_context`, `investigate_area` |
| Geocoding | `geocode_location`, `fly_to` |
| Favorites | `save_favorite`, `list_favorites`, `update_favorite`, `remove_favorite` |
| Filters | `set_filter`, `clear_filter`, `get_plugin_filters` |

## Data Sources (via Data Engine)
- Aviation (OpenSky aircraft positions)
- Maritime (AIS vessel tracking)
- Earthquakes (USGS feed)
- Weather (OpenWeatherMap radar)
- ISS (International Space Station tracking)
- Conflicts/Protests (ACLED data)
- GPS Jamming
- Traffic Cameras (WSDOT, Caltrans, GDOT, TFL, NY511, NCDOT)
- Military Bases (static GeoJSON)
- Any custom plugin from the marketplace

## Config Keys
| Key | Default | Description |
|-----|---------|-------------|
| `WWV_URL` | `http://localhost:3000` | WWV frontend URL |
| `WWV_ENGINE_URL` | `http://localhost:5000` | Data Engine URL |
| `WWV_API_KEY` | (empty) | API key from WWV setup page |
