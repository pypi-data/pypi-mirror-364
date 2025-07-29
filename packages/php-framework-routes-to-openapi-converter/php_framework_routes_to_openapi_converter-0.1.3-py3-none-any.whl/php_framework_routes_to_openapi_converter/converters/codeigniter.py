"""CodeIgniter framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class CodeIgniterConverter(RouteConverter):
    """CodeIgniter framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        return route.get("route", route.get("uri", ""))
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        method = route.get("method", "GET")
        methods = method if isinstance(method, list) else [method]
        return [m.lower() for m in methods]
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        return route.get("controller") or route.get("action") or "CodeIgniter Route"
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        controller = route.get("controller")
        return [controller] if controller else [] 