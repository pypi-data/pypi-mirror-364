"""Yii framework route converter."""
from typing import Dict, List, Any
from php_framework_routes_to_openapi_converter.converters.base import RouteConverter


class YiiConverter(RouteConverter):
    """Yii framework route converter."""
    
    def extract_path(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Yii route converter not implemented")
    
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Yii route converter not implemented")
    
    def extract_summary(self, route: Dict[str, Any]) -> str:
        raise NotImplementedError("Yii route converter not implemented")
    
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("Yii route converter not implemented")
