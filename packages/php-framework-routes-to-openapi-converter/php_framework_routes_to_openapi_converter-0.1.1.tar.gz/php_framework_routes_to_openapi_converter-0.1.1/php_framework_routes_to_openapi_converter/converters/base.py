"""Abstract base class for framework-specific route converters."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class RouteConverter(ABC):
    """Abstract base class for framework-specific route converters."""
    
    @abstractmethod
    def extract_path(self, route: Dict[str, Any]) -> str:
        """Extract the path/URI from route definition."""
        pass
    
    @abstractmethod
    def extract_methods(self, route: Dict[str, Any]) -> List[str]:
        """Extract HTTP methods from route definition."""
        pass
    
    @abstractmethod
    def extract_summary(self, route: Dict[str, Any]) -> str:
        """Extract summary/description for the route."""
        pass
    
    @abstractmethod
    def extract_tags(self, route: Dict[str, Any]) -> List[str]:
        """Extract tags for grouping routes."""
        pass 