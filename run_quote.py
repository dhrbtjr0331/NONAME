import uvicorn
import sys
import os

# Add services to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'quote-service'))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8003, 
        reload=True,
        reload_dirs=["./services/quote-service"]
    )