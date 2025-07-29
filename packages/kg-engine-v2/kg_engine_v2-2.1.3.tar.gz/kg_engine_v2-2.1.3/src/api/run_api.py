#!/usr/bin/env python3
"""
Run the Knowledge Graph Engine REST API
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting Knowledge Graph Engine API v2.1.0")
    print(f"📍 Host: {host}:{port}")
    print(f"🔄 Auto-reload: {reload}")
    print(f"📖 API Docs: http://localhost:{port}/docs")
    print(f"📊 OpenAPI: http://localhost:{port}/openapi.json")
    
    # Run the API
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )