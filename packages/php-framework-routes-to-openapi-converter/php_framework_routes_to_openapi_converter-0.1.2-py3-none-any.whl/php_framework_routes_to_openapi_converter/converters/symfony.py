"""Symfony framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class SymfonyConverter(RouteConverter):
    """Symfony framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        return route.get("path", route.get("uri", ""))
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        methods = route.get("methods", [])
        methods = [methods] if isinstance(methods, str) else methods
        return [m.lower() for m in methods if m]
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name") or route.get("controller") or "Symfony Route"
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        controller = route.get("controller")
        return [controller] if controller else [] 