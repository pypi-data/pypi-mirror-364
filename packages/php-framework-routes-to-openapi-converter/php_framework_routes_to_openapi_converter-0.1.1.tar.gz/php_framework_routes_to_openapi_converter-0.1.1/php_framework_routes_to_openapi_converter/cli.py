#!/usr/bin/env python3
"""Framework-agnostic routes to OpenAPI converter CLI."""
import json
import logging
import sys
from pathlib import Path

import typer
import structlog

from .core import (
    convert_routes_to_openapi,
    get_supported_frameworks,
    validate_framework,
)

# Configure logging first
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Configure structlog for CLI output
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.dev.ConsoleRenderer(colors=False, pad_event=20)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    context_class=dict,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def main(
    routes_file: Path = typer.Argument(
        ..., 
        help="Input routes.json file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    framework: str = typer.Argument(
        ..., 
        help="Framework name (laravel, symfony, codeigniter)"
    ),
    output_file: Path = typer.Argument(
        ..., 
        help="Output OpenAPI file"
    ),
):
    """Convert routes.json to OpenAPI specification."""
    # Validate framework using core API
    if not validate_framework(framework):
        supported = ', '.join(get_supported_frameworks())
        logger.error("Unknown framework", 
                    framework=framework, 
                    supported_frameworks=supported)
        raise typer.Exit(1)
    
    try:
        logger.info("Loading routes", file=str(routes_file))
        with open(routes_file) as f:
            routes = json.load(f)
        logger.info("Routes loaded", count=len(routes), framework=framework)
        
        logger.info("Converting routes", routes_count=len(routes))
        spec = convert_routes_to_openapi(routes, framework)
        logger.info("OpenAPI specification generated", paths_count=len(spec["paths"]))

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Saving specification", file=str(output_file))
        with open(output_file, 'w') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        
        logger.info("Conversion completed", 
                   output_file=str(output_file),
                   paths_converted=len(spec['paths']))
        
    except FileNotFoundError as e:
        logger.error("File not found", error=str(e), file=str(routes_file))
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format", error=str(e), file=str(routes_file))
        raise typer.Exit(1)
    except ValueError as e:
        logger.error("Validation error", error=str(e))
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Conversion failed", error=str(e))
        raise typer.Exit(1)


if __name__ == "__main__":
    typer.run(main)
