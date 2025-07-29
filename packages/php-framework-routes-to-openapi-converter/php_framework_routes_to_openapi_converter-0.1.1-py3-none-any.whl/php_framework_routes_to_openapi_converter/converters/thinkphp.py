"""ThinkPHP framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class ThinkPHPConverter(RouteConverter):
    """ThinkPHP framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("ThinkPHP route converter not implemented")
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("ThinkPHP route converter not implemented")
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("ThinkPHP route converter not implemented")
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("ThinkPHP route converter not implemented")
