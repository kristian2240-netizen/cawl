"""C.A.W.L. ↔ WorldWideView bridge — geospatial intelligence via MCP + REST."""

from __future__ import annotations

import json
from typing import Any

import httpx

from . import config

WWV_URL = "http://localhost:3000"
WWV_ENGINE_URL = "http://localhost:5000"
WWV_API_KEY = ""


def _get_api_key() -> str:
    global WWV_API_KEY  # noqa: PLW0603
    if not WWV_API_KEY:
        WWV_API_KEY = config._env("WWV_API_KEY").strip()
    return WWV_API_KEY


def _get_url() -> str:
    return config._env("WWV_URL", WWV_URL).strip()


def _get_engine_url() -> str:
    return config._env("WWV_ENGINE_URL", WWV_ENGINE_URL).strip()


def _headers() -> dict[str, str]:
    key = _get_api_key()
    h = {"Content-Type": "application/json"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


def mcp_call(method: str, params: dict[str, Any] | None = None) -> dict:
    """Send a JSON-RPC request to WWV's MCP endpoint."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{_get_url()}/api/mcp", json=payload, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        return {"error": "WorldWideView not running — start it with: cd C:\\Users\\Kristian\\worldwideview && pnpm dev:all"}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"MCP call failed: {exc}"}


def mcp_tool(name: str, arguments: dict[str, Any] | None = None) -> dict:
    """Call an MCP tool by name."""
    result = mcp_call("tools/call", {"name": name, "arguments": arguments or {}})
    if "error" in result:
        return result
    content = result.get("result", {}).get("content", [])
    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
    return {"result": "\n".join(texts) if texts else result.get("result", {})}


def mcp_list_tools() -> list[dict]:
    """List all available MCP tools."""
    result = mcp_call("tools/list")
    if "error" in result:
        return []
    return result.get("result", {}).get("tools", [])


def mcp_list_resources() -> list[dict]:
    """List all available MCP resources."""
    result = mcp_call("resources/list")
    if "error" in result:
        return []
    return result.get("result", {}).get("resources", [])


def mcp_read_resource(uri: str) -> dict:
    """Read an MCP resource by URI."""
    return mcp_call("resources/read", {"uri": uri})


# ---------------------------------------------------------------------------
# Convenience wrappers for common queries
# ---------------------------------------------------------------------------

def search_entities(query: str, plugin_id: str = "", limit: int = 20) -> dict:
    """Search for geospatial entities via MCP."""
    args: dict[str, Any] = {"query": query, "limit": limit}
    if plugin_id:
        args["pluginId"] = plugin_id
    return mcp_tool("search_entities", args)


def investigate_area(place_name: str, entity_type: str = "", radius_km: int = 100) -> dict:
    """Investigate an area for geospatial activity."""
    args: dict[str, Any] = {"place_name": place_name, "radius_km": radius_km}
    if entity_type:
        args["entity_type"] = entity_type
    return mcp_tool("investigate_area", args)


def geocode_location(query: str) -> dict:
    """Geocode a place name to coordinates."""
    return mcp_tool("geocode_location", {"query": query})


def fly_to(lat: float, lon: float, altitude: float = 500000) -> dict:
    """Fly the globe camera to coordinates."""
    return mcp_tool("pan_globe", {"lat": lat, "lon": lon, "alt": altitude})


def toggle_layer(plugin_id: str, visible: bool | None = None) -> dict:
    """Toggle a data layer on/off."""
    args: dict[str, Any] = {"pluginId": plugin_id}
    if visible is not None:
        args["visible"] = visible
    return mcp_tool("toggle_layer", args)


def get_entity_details(entity_id: str) -> dict:
    """Get full details for a specific entity."""
    return mcp_tool("get_entity_details", {"entityId": entity_id})


def get_plugin_data(plugin_id: str) -> dict:
    """Get current data snapshot from a plugin."""
    return mcp_tool("get_plugin_data", {"pluginId": plugin_id})


def list_plugins() -> dict:
    """List all available WWV plugins."""
    return mcp_tool("list_available_plugins", {})


def get_entities_in_region(north: float, south: float, east: float, west: float,
                           plugin_id: str = "", limit: int = 100) -> dict:
    """Get entities within a bounding box."""
    args: dict[str, Any] = {"north": north, "south": south, "east": east, "west": west, "limit": limit}
    if plugin_id:
        args["pluginId"] = plugin_id
    return mcp_tool("get_entities_in_region", args)


def get_globe_context() -> dict:
    """Get current globe state context."""
    return mcp_tool("get_globe_context", {})


# ---------------------------------------------------------------------------
# Direct REST (no MCP, for simpler queries)
# ---------------------------------------------------------------------------

def rest_search(query: str, plugin_id: str = "", limit: int = 20) -> dict:
    """Direct REST search against WWV v1 API."""
    params: dict[str, Any] = {"q": query, "limit": limit}
    if plugin_id:
        params["pluginId"] = plugin_id
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{_get_url()}/api/v1/entities/search", params=params, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"REST search failed: {exc}"}


def rest_region(north: float, south: float, east: float, west: float,
                plugin_id: str = "", limit: int = 100) -> dict:
    """Direct REST bounding-box query against WWV v1 API."""
    params: dict[str, Any] = {"north": north, "south": south, "east": east, "west": west, "limit": limit}
    if plugin_id:
        params["pluginId"] = plugin_id
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(f"{_get_url()}/api/v1/entities/region", params=params, headers=_headers())
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"REST region query failed: {exc}"}


def engine_snapshot(plugin_id: str) -> dict:
    """Get raw data from the Data Engine REST endpoint."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{_get_engine_url()}/api/{plugin_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Engine snapshot failed: {exc}"}


def engine_manifest() -> dict:
    """Get the Data Engine's plugin manifest."""
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(f"{_get_engine_url()}/manifest")
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Engine manifest failed: {exc}"}


def health_check() -> dict:
    """Check if WWV is running and healthy."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{_get_url()}/api/health")
            return resp.json()
    except Exception as exc:  # noqa: BLE001
        return {"status": "offline", "error": str(exc)}


def status() -> dict:
    """Get full WWV connection status."""
    health = health_check()
    tools = mcp_list_tools()
    resources = mcp_list_resources()
    return {
        "connected": health.get("status") == "ok",
        "health": health,
        "mcp_tools": len(tools),
        "mcp_resources": len(resources),
        "api_key_set": bool(_get_api_key()),
        "url": _get_url(),
        "engine_url": _get_engine_url(),
    }
