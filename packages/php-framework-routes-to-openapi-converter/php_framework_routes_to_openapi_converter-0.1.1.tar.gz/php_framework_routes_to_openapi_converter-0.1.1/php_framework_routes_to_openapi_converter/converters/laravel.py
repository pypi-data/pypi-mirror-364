"""Laravel framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class LaravelConverter(RouteConverter):
    """Laravel framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        return route.get("uri", "")
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        methods = route.get("methods", [])
        if isinstance(methods, list):
            return [m.lower() for m in methods if m]
        # Fallback for legacy "method" field (string with | separator)
        method_str = route.get("method", "")
        return [m.strip().lower() for m in method_str.split("|") if m.strip()] if method_str else []
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name") or route.get("action") or "Laravel Route"
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        action = route.get("action")
        return [action] if action else [] 