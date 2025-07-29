"""Core API for PHP framework routes to OpenAPI conversion."""
from typing import Dict, List, Any, Optional

from php_framework_detector.core.models import FrameworkType
from .converters import (
    RouteConverter,
    LaravelConverter,
    SymfonyConverter,
    CodeIgniterConverter,
    CakePHPConverter,
    DrupalConverter,
    DrushConverter,
    FastRouteConverter,
    FatFreeConverter,
    FuelConverter,
    LaminasConverter,
    PhalconConverter,
    PhpixieConverter,
    PopphpConverter,
    SlimConverter,
    ThinkPHPConverter,
    YiiConverter,
    ZendframeworkConverter,
)


def get_converter(framework: str) -> RouteConverter:
    """Get the appropriate converter for the framework.
    
    Args:
        framework: The PHP framework name (case-insensitive)
        
    Returns:
        RouteConverter: The appropriate converter instance
        
    Raises:
        ValueError: If the framework is not supported
        
    Example:
        >>> converter = get_converter("laravel")
        >>> isinstance(converter, LaravelConverter)
        True
    """
    converters = {
        FrameworkType.LARAVEL: LaravelConverter(),
        FrameworkType.SYMFONY: SymfonyConverter(), 
        FrameworkType.CODEIGNITER: CodeIgniterConverter(),
        FrameworkType.CAKEPHP: CakePHPConverter(),
        FrameworkType.YII: YiiConverter(),
        FrameworkType.THINKPHP: ThinkPHPConverter(),
        FrameworkType.SLIM: SlimConverter(),
        FrameworkType.FATFREE: FatFreeConverter(),
        FrameworkType.FASTROUTE: FastRouteConverter(),
        FrameworkType.FUEL: FuelConverter(),
        FrameworkType.PHALCON: PhalconConverter(),
        FrameworkType.PHPIXIE: PhpixieConverter(),
        FrameworkType.POPPHP: PopphpConverter(),
        FrameworkType.LAMINAS: LaminasConverter(),
        FrameworkType.ZENDFRAMEWORK: ZendframeworkConverter(),
        FrameworkType.DRUPAL: DrupalConverter(),
        FrameworkType.DRUSH: DrushConverter(),
    }
    return converters[FrameworkType(framework)] 


def convert_routes_to_openapi(
    routes: List[Dict[str, Any]], 
    framework: str, 
    api_title: Optional[str] = "API Specification", 
    api_version: Optional[str] = "1.0.0"
) -> Dict[str, Any]:
    """Convert routes to OpenAPI specification using framework-specific converter.
    
    Args:
        routes: List of route dictionaries from the framework
        framework: The PHP framework name
        api_title: Optional custom API title (defaults to "{Framework} API")
        api_version: API version string (defaults to "1.0.0")
        
    Returns:
        Dict containing the complete OpenAPI 3.0 specification
        
    Raises:
        ValueError: If the framework is not supported
        
    Example:
        >>> routes = [{"uri": "/users", "methods": ["GET"], "name": "users.index"}]
        >>> spec = convert_routes_to_openapi(routes, "laravel", "My API", "2.0.0")
        >>> spec["openapi"]
        '3.0.0'
        >>> spec["info"]["title"]
        'My API'
    """
    converter = get_converter(framework)
    paths = {}
    
    for route in routes:
        path = converter.extract_path(route)
        if not path:
            continue
            
        methods = converter.extract_methods(route)
        summary = converter.extract_summary(route)
        tags = converter.extract_tags(route)
        
        if path not in paths:
            paths[path] = {}
            
        for method in methods:
            paths[path][method] = {
                "summary": summary,
                "tags": tags,
                "responses": {"200": {"description": "Success"}}
            }

    return {
        "openapi": "3.0.0",
        "info": {"title": api_title, "version": api_version},
        "paths": paths
    }


def get_supported_frameworks() -> List[str]:
    """Get list of supported PHP frameworks.
    
    Returns:
        List of supported framework names in lowercase
        
    Example:
        >>> frameworks = get_supported_frameworks()
        >>> "laravel" in frameworks
        True
    """
    return ["laravel", "symfony", "codeigniter"]


def validate_framework(framework: str) -> bool:
    """Validate if a framework is supported.
    
    Args:
        framework: The framework name to validate
        
    Returns:
        True if the framework is supported, False otherwise
        
    Example:
        >>> validate_framework("laravel")
        True
        >>> validate_framework("unknown")
        False
    """
    return framework.lower() in get_supported_frameworks() 