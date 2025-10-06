"""
Adaptive AI Compliance Engine for Creative Industries
Main FastAPI application entry point
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

app = FastAPI(
    title="Music Police - AI Compliance Engine",
    description="Adaptive AI Compliance Engine for Creative Industries",
    version="1.0.0"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    """Root endpoint - returns the dashboard"""
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get("/upload")
async def upload_page():
    """Simple upload page for testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Music Police - Upload</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px;
                   margin: 0 auto; padding: 20px; background: #1a1d29;
                   color: white; }
            .header { text-align: center; color: #fff; }
            .upload-area { border: 2px dashed #667eea; padding: 40px;
                          text-align: center; margin: 20px 0;
                          background: #232740; border-radius: 12px; }
            .btn { background: linear-gradient(135deg, #f093fb 0%,
                                                    #f5576c 100%);
                   color: white; padding: 10px 20px; border: none;
                   border-radius: 5px; cursor: pointer; }
            .btn:hover { transform: translateY(-2px); }
            .result { margin: 20px 0; padding: 15px; background: #232740;
                     border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎼 Music Police</h1>
            <h2>AI Compliance Engine Upload</h2>
            <p><a href="/" style="color: #667eea;">← Back to Dashboard</a></p>
        </div>
        <div class="upload-area">
            <h3>Upload Audio File for Compliance Check</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="audioFile" accept=".mp3,.wav,.flac,.m4a"
                       required style="margin: 10px; padding: 10px;">
                <br><br>
                <button type="submit" class="btn">Analyze Audio</button>
            </form>
        </div>
        <div id="result" class="result" style="display:none;">
            <h3>Analysis Results</h3>
            <div id="resultContent"></div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener(
                'submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                const fileInput = document.getElementById('audioFile');
                formData.append('file', fileInput.files[0]);
                try {
                    const response = await fetch('/analyze-audio', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultContent').innerHTML =
                        '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Music Police API"}


@app.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file for compliance
    This is a placeholder - will be implemented with actual ML models
    """
    if not file.filename.lower().endswith(
            ('.mp3', '.wav', '.flac', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Save uploaded file temporarily
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Placeholder analysis results
    analysis_result = {
        "filename": file.filename,
        "file_size": len(content),
        "status": "analyzed",
        "compliance_score": 85.5,
        "issues_detected": [
            {
                "type": "potential_copyright",
                "severity": "medium",
                "confidence": 0.65,
                "description": "Detected similarity to existing copyrighted " +
                               "material"
            }
        ],
        "recommendations": [
            "Review potential copyright similarities",
            "Consider modifying melodic patterns in measures 12-16"
        ],
        "metadata": {
            "duration_seconds": "estimated_180",
            "sample_rate": "44100",
            "channels": "stereo"
        }
    }

    # Clean up uploaded file
    os.remove(file_path)

    return analysis_result


@app.get("/api/rules")
async def get_compliance_rules():
    """Get current compliance rules"""
    return {
        "copyright_rules": {
            "similarity_threshold": 0.7,
            "enabled": True
        },
        "bias_detection": {
            "enabled": True,
            "categories": ["gender", "race", "age"]
        },
        "content_filtering": {
            "explicit_content": True,
            "hate_speech": True
        }
    }


@app.get("/api/recent-analyses")
async def get_recent_analyses():
    """Get recent analysis results for dashboard"""
    # Generate mock data for demonstration
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


@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
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


@app.get("/api/compliance-details/{analysis_type}")
async def get_compliance_details(analysis_type: str):
    """Get detailed compliance information for a specific analysis type"""
    if analysis_type not in ["copyright", "bias", "content_filter"]:
        raise HTTPException(status_code=404,
                            detail="Analysis type not found")
    details = {
        "copyright": {
            "description": "Detects potential copyright infringement",
            "last_updated": datetime.now().isoformat(),
            "rules_count": 15,
            "accuracy": 94.2,
            "recent_matches": [
                {"similarity": 0.87, "source": "Popular Song Database"},
                {"similarity": 0.73, "source": "Classical Music Archive"}
            ]
        },
        "bias": {
            "description": "Analyzes content for potential bias",
            "last_updated": datetime.now().isoformat(),
            "categories_checked": ["gender", "race", "age", "religion"],
            "accuracy": 89.1,
            "recent_flags": [
                {"category": "gender", "confidence": 0.82},
                {"category": "age", "confidence": 0.67}
            ]
        },
        "content_filter": {
            "description": "Filters explicit and inappropriate content",
            "last_updated": datetime.now().isoformat(),
            "filter_types": ["explicit_language", "hate_speech", "violence"],
            "accuracy": 96.8,
            "recent_blocks": [
                {"type": "explicit_language", "confidence": 0.94},
                {"type": "hate_speech", "confidence": 0.78}
            ]
        }
    }

    return details.get(analysis_type, {})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
