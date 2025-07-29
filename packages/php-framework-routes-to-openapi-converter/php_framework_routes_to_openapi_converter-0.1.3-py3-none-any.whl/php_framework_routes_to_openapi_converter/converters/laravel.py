"""Laravel framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class LaravelConverter(RouteConverter):
    """Laravel framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        return route.get("uri", "")
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        """
        >>> LaravelConverter().extract_methods({"method": "GET"})
        ['get']
        
        >>> LaravelConverter().extract_methods({"method": "GET|HEAD"})
        ['get', 'head']
        
        >>> LaravelConverter().extract_methods({"method": "HEAD"})
        ['head']
        
        >>> LaravelConverter().extract_methods({"method": "POST"})
        ['post']
        """
        
        method = route.get("method", "")
        if method:
            return [m.strip().lower() for m in method.split("|") if m.strip()]
        return []
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        return route.get("name") or route.get("action") or "Laravel Route"
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        action = route.get("action")
        return [action] if action else [] 