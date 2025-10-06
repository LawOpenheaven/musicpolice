"""
Music Police - Adaptive AI Compliance Engine
Enhanced FastAPI application with structured backend
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import logging
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings
from app.api.routes import router as api_router
from app.db.database import init_database, test_database_connection

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# In-memory storage for API call monitoring
# (in production, use Redis or database)
api_call_history: Dict[str, Any] = {}

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Adaptive AI Compliance Engine for Creative Industries",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Monitoring Middleware


@app.middleware("http")
async def api_monitoring_middleware(request: Request, call_next):
    """Middleware to monitor all API calls and responses"""
    # Skip monitoring for debug endpoints to prevent infinite loops
    if request.url.path.startswith("/debug/"):
        return await call_next(request)

    start_time = time.time()

    # Generate unique request ID
    request_id = f"{int(time.time() * 1000)}_{hash(request.url.path) % 10000}"

    # Log incoming request
    request_info = {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }

    # Log request body for POST/PUT requests (excluding file uploads)
    content_type = request.headers.get("content-type", "")
    if (request.method in ["POST", "PUT", "PATCH"] and
            "multipart/form-data" not in content_type):
        try:
            body = await request.body()
            if body:
                try:
                    request_info["body"] = json.loads(body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Truncate large bodies
                    request_info["body"] = body.decode()[:500]
        except Exception as e:
            request_info["body_error"] = str(e)

    logger.info("API REQUEST [%s] %s %s",
                request_id, request.method, request.url.path)
    logger.debug("Request details: %s",
                 json.dumps(request_info, indent=2))

    # Store request info
    api_call_history[request_id] = {
        "request": request_info,
        "response": None,
        "processing_time": None,
        "status": "processing"
    }

    # Process request
    try:
        response = await call_next(request)
        processing_time = time.time() - start_time

        # Log response
        response_info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "processing_time_ms": round(processing_time * 1000, 2)
        }

        # Update stored info
        api_call_history[request_id]["response"] = response_info
        api_call_history[request_id]["processing_time"] = processing_time
        api_call_history[request_id]["status"] = "completed"

        # Log response
        status_emoji = "SUCCESS" if response.status_code < 400 else "ERROR"
        logger.info("%s API RESPONSE [%s] %s - %.3fs",
                    status_emoji, request_id, response.status_code,
                    processing_time)
        logger.debug("Response details: %s",
                     json.dumps(response_info, indent=2))

        # Add request ID to response headers for debugging
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        processing_time = time.time() - start_time
        error_info = {
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time_ms": round(processing_time * 1000, 2)
        }

        # Update stored info
        api_call_history[request_id]["response"] = error_info
        api_call_history[request_id]["processing_time"] = processing_time
        api_call_history[request_id]["status"] = "error"

        logger.error("API ERROR [%s] %s - %.3fs",
                     request_id, str(e), processing_time)
        logger.debug("Error details: %s",
                     json.dumps(error_info, indent=2))

        raise

# Mount static files and setup templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routes under /api prefix
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup tasks"""
    print("🎼 Starting Music Police - AI Compliance Engine...")

    # Test database connection
    if test_database_connection():
        print("✅ Database connection successful")

        # Initialize database with tables and default data
        init_database()
        print("✅ Database initialization complete")
    else:
        print("❌ Database connection failed - some features may not work")

    # Start background workers
    try:
        from app.workers.tasks import start_background_workers
        await start_background_workers()
        print("✅ Background workers started")
    except Exception as e:
        print(f"⚠️ Background workers failed to start: {e}")

    print(f"🚀 Server starting on {settings.HOST}:{settings.PORT}")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page - preserved from original implementation"""
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Music Police Dashboard</title></head>
            <body>
                <h1>🎼 Music Police - AI Compliance Engine</h1>
                <p>Dashboard template not found. Please ensure dashboard.html exists in templates/</p>
        <p><a href="/upload">Go to Upload Page</a></p>
        <p><a href="/api/health">Check API Health</a></p>
        <p><a href="/api-monitor">API Monitor</a></p>
            </body>
        </html>
        """)


@app.get("/api-monitor", response_class=HTMLResponse)
async def api_monitor_page():
    """API monitoring dashboard page"""
    try:
        with open("templates/api_monitor.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>API Monitor</title></head>
            <body>
                <h1>🎼 API Monitor</h1>
                <p>API monitor template not found. Please ensure api_monitor.html exists in templates/</p>
                <p><a href="/">Back to Dashboard</a></p>
            </body>
        </html>
        """)


@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """Enhanced upload page with new API integration"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Music Police - Upload</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #1a1d29;
                color: white;
            }
            .header { text-align: center; color: #fff; }
            .upload-area {
                border: 2px dashed #667eea;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                background: #232740;
                border-radius: 12px;
            }
            .btn {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .btn:hover { transform: translateY(-2px); }
            .result {
                margin: 20px 0;
                padding: 15px;
                background: #232740;
                border-radius: 5px;
            }
            .lyrics-input {
                width: 100%;
                height: 100px;
                margin: 10px 0;
                padding: 10px;
                background: #1a1d29;
                color: white;
                border: 1px solid #667eea;
                border-radius: 5px;
            }
            .loading {
                display: none;
                text-align: center;
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎼 Music Police</h1>
            <h2>AI Compliance Engine Upload</h2>
            <p><a href="/" style="color: #667eea;">← Back to Dashboard</a></p>
            <p><a href="/api-monitor" style="color: #667eea;">📊 API Monitor</a></p>
        </div>

        <div class="upload-area">
            <h3>Upload Audio File for Compliance Check</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="audioFile" accept=".mp3,.wav,.flac,.m4a,.ogg"
                       required style="margin: 10px; padding: 10px;">
                <br>
                <textarea id="lyricsInput" class="lyrics-input"
                         placeholder="Optional: Enter lyrics for bias analysis..."></textarea>
                <br>
                <button type="submit" class="btn">Analyze Audio</button>
            </form>

            <div id="loading" class="loading">
                <p>🔍 Analyzing audio for compliance issues...</p>
                <p>This may take a few moments...</p>
            </div>
        </div>

        <div id="result" class="result" style="display:none;">
            <h3>Analysis Results</h3>
            <div id="resultContent"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData();
                const fileInput = document.getElementById('audioFile');
                const lyricsInput = document.getElementById('lyricsInput');

                if (!fileInput.files[0]) {
                    alert('Please select an audio file');
                    return;
                }

                formData.append('file', fileInput.files[0]);
                if (lyricsInput.value.trim()) {
                    formData.append('lyrics', lyricsInput.value.trim());
                }

                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';

                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    // Hide loading
                    document.getElementById('loading').style.display = 'none';

                    if (response.ok) {
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('resultContent').innerHTML = formatResult(result);
                    } else {
                        alert('Error: ' + (result.detail || 'Analysis failed'));
                    }

                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error: ' + error.message);
                }
            });

            function formatResult(result) {
                let html = `
                    <div style="margin-bottom: 20px;">
                        <h4>📊 Compliance Score: ${(result.compliance_score * 100).toFixed(1)}%</h4>
                        <div style="background: #1a1d29; padding: 10px; border-radius: 5px;">
                            <strong>File:</strong> ${result.filename}<br>
                            <strong>Analysis ID:</strong> ${result.id}<br>
                            ${result.cached ? '<strong>⚡ Cached Result</strong><br>' : ''}
                        </div>
                    </div>
                `;

                if (result.issues && result.issues.length > 0) {
                    html += '<h4>⚠️ Issues Detected:</h4><ul>';
                    result.issues.forEach(issue => {
                        html += `<li><strong>${issue.type}</strong> (${issue.severity}): ${issue.detail}</li>`;
                    });
                    html += '</ul>';
                } else {
                    html += '<h4>✅ No Issues Detected</h4>';
                }

                if (result.recommendations && result.recommendations.length > 0) {
                    html += '<h4>💡 Recommendations:</h4><ul>';
                    result.recommendations.forEach(rec => {
                        html += `<li>${rec}</li>`;
                    });
                    html += '</ul>';
                }

                return html;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Music Police API", "version": settings.VERSION}


@app.get("/debug/api-calls")
async def get_api_call_history(limit: int = 50, status: str = None):
    """Debug endpoint to view recent API calls and responses"""
    if not settings.DEBUG:
        return {"error": "Debug endpoints are only available in development mode"}

    # Filter and sort API calls
    calls = list(api_call_history.values())

    if status:
        calls = [call for call in calls if call.get("status") == status]

    # Sort by timestamp (most recent first)
    calls.sort(key=lambda x: x["request"]["timestamp"], reverse=True)

    # Limit results
    calls = calls[:limit]

    return {
        "total_calls": len(api_call_history),
        "filtered_calls": len(calls),
        "calls": calls,
        "status_filter": status,
        "limit": limit
    }


@app.get("/debug/api-calls/{request_id}")
async def get_specific_api_call(request_id: str):
    """Get detailed information about a specific API call"""
    if not settings.DEBUG:
        return {"error": "Debug endpoints are only available in development mode"}

    if request_id not in api_call_history:
        return {"error": "Request ID not found"}

    return {
        "request_id": request_id,
        "call_details": api_call_history[request_id]
    }


@app.delete("/debug/api-calls")
async def clear_api_call_history():
    """Clear the API call history (debug only)"""
    if not settings.DEBUG:
        return {"error": "Debug endpoints are only available in development mode"}

    cleared_count = len(api_call_history)
    api_call_history.clear()

    return {
        "message": f"Cleared {cleared_count} API call records",
        "remaining_calls": len(api_call_history)
    }

# Legacy endpoints for backward compatibility with existing dashboard


@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """Legacy endpoint for dashboard statistics"""
    return {
        "total_analyses": 1243,
        "compliance_scores": {
            "copyright": 85,
            "bias": 92,
            "content_filter": 88
        },
        "queue_metrics": [
            {"label": "Pending", "value": 2716, "percentage": 85},
            {"label": "Processing", "value": 1094, "percentage": 65},
            {"label": "Completed", "value": 8058, "percentage": 95},
            {"label": "Failed", "value": 237, "percentage": 15}
        ],
        "trend_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
            "values": [120, 190, 300, 500, 200, 300, 450, 600]
        }
    }


@app.get("/api/recent-analyses")
async def get_recent_analyses_legacy():
    """Legacy endpoint for recent analyses"""
    from datetime import timedelta
    import random

    analyses = []
    analysis_types = ['copyright', 'bias', 'content_filter']
    for i in range(10):
        analysis_date = datetime.now() - timedelta(days=random.randint(0, 7))
        analyses.append({
            "id": i + 1,
            "type": random.choice(analysis_types),
            "score": random.randint(70, 98),
            "status": random.choice(["completed", "processing", "failed"]),
            "filename": f"audio_sample_{i+1}.mp3",
            "timestamp": analysis_date.isoformat(),
            "issues_count": random.randint(0, 3),
            "processing_time": random.uniform(1.2, 8.5)
        })
    return {"analyses": analyses, "total": len(analyses)}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
