# 🎼 Music Police - AI-Powered Music Compliance Engine

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive web application that analyzes audio files for copyright infringement, bias detection, and content compliance using advanced AI and machine learning techniques. Built with FastAPI, PostgreSQL, and modern web technologies.

## ✨ Features

### 🔍 **Advanced Compliance Analysis**

- **Copyright Detection**: Sophisticated similarity analysis using librosa, MFCC, chroma, and spectral features
- **Bias Detection**: AI-powered analysis of lyrics for toxicity, racial bias, gender bias, and hate speech
- **Content Filtering**: Detection of explicit content and inappropriate language
- **Visual Analytics**: Interactive dashboards with detailed bias and similarity visualizations
- **Real-time Processing**: Fast analysis with progress tracking and background workers

### 🎯 **Key Capabilities**

- **Audio Transcription**: Automatic lyrics extraction using OpenAI Whisper
- **Database Integration**: PostgreSQL backend with comprehensive data storage
- **Settings Management**: Configurable compliance rules and system settings
- **API Endpoints**: RESTful API for integration with other systems
- **Background Processing**: Asynchronous analysis with worker queues
- **File Management**: Secure upload and storage of audio files

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/downloads)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/LawOpenheaven/musicpolice.git
   cd musicpolice
   ```

2. **Set up Python environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up the database**

   ```bash
   # Create PostgreSQL database
   createdb musicpolice_db

   # Or using psql:
   psql -U postgres
   CREATE DATABASE musicpolice_db;
   \q
   ```

4. **Configure environment**

   ```bash
   # Copy example environment file
   cp env.example .env

   # Edit .env with your database credentials
   # Example .env content:
   DATABASE_URL=postgresql://username:password@localhost:5432/musicpolice_db
   ```

5. **Initialize database**

   ```bash
   # This creates all tables and default data
   python database_init.py
   ```

6. **Run the application**

   ```bash
   # Start the development server
   python -m app.main

   # Or with auto-reload for development
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the dashboard**
   Open your browser and go to: `http://localhost:8000`

## 📁 Project Structure

```
musicpolice/
├── app/                           # Main application code
│   ├── api/                      # API routes and endpoints
│   │   └── routes.py             # FastAPI route definitions
│   ├── core/                     # Core configuration
│   │   └── config.py             # Application configuration
│   ├── db/                       # Database models and session management
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── session.py            # Database session management
│   │   └── database.py           # Database initialization
│   ├── services/                 # Business logic services
│   │   ├── analyzer.py           # Main analysis orchestrator
│   │   ├── similarity_detector.py # Copyright detection logic
│   │   ├── lyrics_bias.py        # Bias detection algorithms
│   │   ├── transcription.py      # Audio transcription service
│   │   ├── rules.py              # Compliance rules management
│   │   └── settings.py           # System settings management
│   ├── workers/                  # Background task workers
│   │   └── tasks.py              # Async task processing
│   └── main.py                   # FastAPI application entry point
├── static/                       # Frontend assets
│   ├── dashboard.css             # Main stylesheet with dark theme
│   ├── dashboard.js              # Main JavaScript functionality
│   └── bias-similarity-visualization.js # Advanced visualization components
├── templates/                    # HTML templates
│   ├── dashboard.html            # Main dashboard interface
│   └── api_monitor.html          # API monitoring interface
├── migrations/                   # Database migrations
│   ├── env.py                    # Alembic environment
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration files
├── requirements.txt              # Python dependencies
├── config.py                     # Application configuration
├── database_init.py              # Database initialization script
├── main.py                       # Alternative entry point
├── env.example                   # Environment variables template
├── alembic.ini                   # Alembic configuration
├── package.json                  # Node.js configuration
├── LICENSE                       # MIT License
└── README.md                     # This file
```

## 🔧 Configuration

### Database Settings

The application uses PostgreSQL for data storage. Configure your database connection in the `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/musicpolice_db
```

### Compliance Rules

Configure compliance thresholds through the web interface or API:

- **Copyright Detection**: Similarity threshold (default: 0.7)
- **Bias Detection**: Toxicity threshold (default: 0.4)
- **Content Filtering**: Explicit content threshold (default: 0.6)

### System Settings

Manage system-wide settings including:

- File size limits (default: 100MB)
- Analysis timeouts (default: 300 seconds)
- API rate limiting (default: 100 requests/minute)
- Security settings (authentication, encryption)

## 🎵 Supported Audio Formats

- **MP3** - Most common format
- **WAV** - Uncompressed audio
- **FLAC** - Lossless compression
- **M4A** - Apple audio format
- **OGG** - Open source format

## 🔌 API Endpoints

### Analysis

- `POST /api/analyze` - Analyze audio file for compliance
- `GET /api/analyses` - Get paginated analysis results
- `GET /api/analyses/{id}` - Get specific analysis details
- `GET /api/analyses/{id}/audio` - Stream audio file for playback
- `GET /api/analyses/{id}/bias-details` - Get detailed bias analysis
- `GET /api/analyses/{id}/similarity-details` - Get similarity analysis details

### Compliance Rules

- `GET /api/rules` - Get all compliance rules
- `POST /api/rules` - Update compliance rules
- `PUT /api/rules/{id}` - Update specific rule
- `DELETE /api/rules/{id}` - Delete compliance rule

### System Settings

- `GET /api/settings` - Get all system settings
- `POST /api/settings` - Update system settings
- `GET /api/settings/{key}` - Get specific setting

### Dashboard & Statistics

- `GET /api/dashboard-stats` - Get dashboard statistics
- `GET /api/recent-analyses` - Get recent analyses
- `GET /api/health` - Health check endpoint

### Interactive API Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/docs
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Check types
mypy app/

# Run all checks
black app/ && flake8 app/ && mypy app/
```

## 🎯 How It Works

### 1. Audio Upload & Processing

- User uploads audio file through web interface
- File is validated for format and size
- Audio fingerprint is generated using librosa
- File is stored securely for analysis

### 2. Copyright Detection

- Extract audio features (MFCC, chroma, spectral)
- Compare against existing database of audio fingerprints
- Calculate similarity scores using cosine similarity
- Identify potential copyright violations

### 3. Bias Detection

- Transcribe audio to text using Whisper
- Analyze lyrics using transformer models
- Detect toxicity, racial bias, gender bias
- Provide detailed word-level and line-level analysis

### 4. Compliance Scoring

- Apply configurable thresholds
- Calculate weighted compliance score
- Generate detailed recommendations
- Store results in database

### 5. Visualization & Reporting

- Interactive dashboard with real-time updates
- Visual bias analysis with highlighted problematic words
- Similarity analysis with comparison views
- Export capabilities for reports

## 🔍 Advanced Features

### Visual Bias Analysis

- **Word Highlighting**: Problematic words are highlighted with color coding
- **Category Breakdown**: Detailed analysis by bias type (racial, gender, toxicity)
- **Line-by-Line Analysis**: Individual line scoring and recommendations
- **Interactive Tooltips**: Hover for detailed explanations

### Similarity Detection

- **Audio Fingerprinting**: Advanced feature extraction using librosa
- **Database Comparison**: Efficient similarity search across stored files
- **Visual Comparison**: Side-by-side analysis of similar sections
- **Confidence Scoring**: Detailed similarity metrics and confidence levels

### System Management

- **Real-time Settings**: Update compliance rules without restart
- **Background Processing**: Async analysis with progress tracking
- **File Management**: Automatic cleanup and organization
- **API Monitoring**: Built-in monitoring and health checks

## 🐛 Troubleshooting

### Common Issues

**Database Connection Issues**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U username -d musicpolice_db -c "SELECT 1;"

# Check environment variables
cat .env
```

**Python Import Issues**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**Port Already in Use**

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

**Audio Processing Issues**

```bash
# Check librosa installation
python -c "import librosa; print(librosa.__version__)"

# Check audio file format
file audio_file.mp3

# Test with sample file
python -c "import librosa; y, sr = librosa.load('test.mp3'); print('Success')"
```

## 📊 Performance Optimization

### Database Optimization

- Indexed audio fingerprints for fast similarity search
- Connection pooling for concurrent requests
- Query optimization for large datasets

### Audio Processing

- Efficient feature extraction using librosa
- Caching of processed audio fingerprints
- Background processing for large files

### Frontend Optimization

- Lazy loading of analysis results
- Efficient DOM updates
- Responsive design for all devices

## 🔒 Security Features

- **File Validation**: Strict file type and size validation
- **SQL Injection Protection**: Parameterized queries with SQLAlchemy
- **XSS Protection**: Sanitized user input and output
- **CSRF Protection**: Built-in FastAPI security features
- **Secure File Storage**: Encrypted file storage options

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test your changes**
   ```bash
   pytest
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Test on multiple Python versions

## 📋 Requirements

### Core Dependencies

- **FastAPI** - Modern web framework for APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Advanced open source database
- **Librosa** - Audio and music signal processing
- **Transformers** - State-of-the-art NLP models
- **Whisper** - Automatic speech recognition
- **Alembic** - Database migration tool
- **Uvicorn** - ASGI server implementation

### Development Dependencies

- **Pytest** - Testing framework
- **Black** - Code formatter
- **Flake8** - Linter
- **MyPy** - Static type checker

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - For audio transcription capabilities
- **Hugging Face Transformers** - For bias detection models
- **Librosa** - For audio analysis and feature extraction
- **FastAPI** - For the excellent web framework
- **SQLAlchemy** - For database ORM capabilities

## 📞 Support & Community

### Getting Help

- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Issues**: Create an issue on GitHub with detailed information
- 💬 **Discussions**: Use GitHub Discussions for questions and ideas
- 📧 **Contact**: Reach out through GitHub profile

### Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Error messages and stack traces
- Steps to reproduce
- Sample audio files (if applicable)

## 🚀 Roadmap

### Planned Features

- [ ] **Machine Learning Improvements**: Enhanced bias detection models
- [ ] **API Rate Limiting**: Advanced rate limiting and throttling
- [ ] **User Authentication**: Multi-user support with roles
- [ ] **Batch Processing**: Bulk audio file analysis
- [ ] **Export Features**: PDF reports and data export
- [ ] **Mobile App**: React Native mobile application
- [ ] **Cloud Deployment**: Docker and Kubernetes support
- [ ] **Advanced Analytics**: Machine learning insights and trends

### Performance Improvements

- [ ] **Caching Layer**: Redis integration for improved performance
- [ ] **CDN Integration**: Global content delivery
- [ ] **Database Sharding**: Horizontal scaling support
- [ ] **Microservices**: Service decomposition for scalability

---

**Made with ❤️ for music compliance and AI-powered analysis**

_Music Police - Ensuring ethical and compliant music content through advanced AI technology_
