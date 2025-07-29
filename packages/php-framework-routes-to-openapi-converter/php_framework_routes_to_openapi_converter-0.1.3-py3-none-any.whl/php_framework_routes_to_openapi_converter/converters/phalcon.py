"""Phalcon framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class PhalconConverter(RouteConverter):
    """Phalcon framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Phalcon route converter not implemented")
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Phalcon route converter not implemented")
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Phalcon route converter not implemented")
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Phalcon route converter not implemented")
