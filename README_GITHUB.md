# 🎼 Music Police - AI-Powered Music Compliance Engine

A comprehensive web application that analyzes audio files for copyright infringement, bias detection, and content compliance using advanced AI and machine learning techniques.

## ✨ Features

### 🔍 **Compliance Analysis**

- **Copyright Detection**: Advanced similarity analysis using librosa and audio fingerprinting
- **Bias Detection**: AI-powered analysis of lyrics for toxicity, racial bias, and gender bias
- **Content Filtering**: Detection of explicit content and inappropriate language
- **Visual Analytics**: Interactive dashboards with detailed bias and similarity visualizations

### 🎯 **Key Capabilities**

- **Real-time Analysis**: Fast processing of audio files with progress tracking
- **Database Integration**: PostgreSQL backend with comprehensive data storage
- **Settings Management**: Configurable compliance rules and system settings
- **API Endpoints**: RESTful API for integration with other systems
- **Background Processing**: Asynchronous analysis with worker queues

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Node.js (optional, for frontend development)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/musicpolice.git
   cd musicpolice
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**

   ```bash
   # Create PostgreSQL database
   createdb musicpolice_db

   # Initialize database with tables and default data
   python database_init.py
   ```

4. **Configure environment**

   ```bash
   # Copy example environment file
   cp env.example .env

   # Edit .env with your database credentials
   nano .env
   ```

5. **Run the application**

   ```bash
   python -m app.main
   ```

6. **Access the dashboard**
   Open your browser and go to: `http://localhost:8000`

## 📁 Project Structure

```
musicpolice/
├── app/                    # Main application code
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core configuration
│   ├── db/                # Database models and session management
│   ├── services/          # Business logic services
│   └── workers/           # Background task workers
├── static/                # Frontend assets
│   ├── dashboard.css      # Main stylesheet
│   ├── dashboard.js       # Main JavaScript
│   └── bias-similarity-visualization.js
├── templates/             # HTML templates
├── migrations/            # Database migrations
├── requirements.txt       # Python dependencies
├── README_GITHUB.md       # This file
└── DEVELOPMENT_SETUP.md   # Development setup guide
```

## 🔧 Configuration

### Database Settings

The application uses PostgreSQL for data storage. Configure your database connection in the `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/musicpolice_db
```

### Compliance Rules

Configure compliance thresholds through the web interface:

- **Copyright Detection**: Similarity threshold (default: 0.7)
- **Bias Detection**: Toxicity threshold (default: 0.4)
- **Content Filtering**: Explicit content threshold (default: 0.6)

### System Settings

Manage system-wide settings including:

- File size limits
- Analysis timeouts
- API rate limiting
- Security settings

## 🎵 Supported Audio Formats

- MP3
- WAV
- FLAC
- M4A
- OGG

## 🔌 API Endpoints

### Analysis

- `POST /api/analyze` - Analyze audio file
- `GET /api/analyses` - Get analysis results
- `GET /api/analyses/{id}` - Get specific analysis

### Compliance Rules

- `GET /api/rules` - Get compliance rules
- `POST /api/rules` - Update compliance rules

### System Settings

- `GET /api/settings` - Get system settings
- `POST /api/settings` - Update system settings

### Dashboard

- `GET /api/dashboard-stats` - Get dashboard statistics
- `GET /api/recent-analyses` - Get recent analyses

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

### Core Dependencies

- FastAPI - Web framework
- SQLAlchemy - Database ORM
- PostgreSQL - Database
- Librosa - Audio processing
- Transformers - AI models for bias detection
- Whisper - Audio transcription

### Development Dependencies

- Pytest - Testing framework
- Black - Code formatting
- Flake8 - Linting
- Alembic - Database migrations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for audio transcription
- Hugging Face Transformers for bias detection models
- Librosa for audio analysis
- FastAPI for the web framework

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the setup guides in the repository

---

**Made with ❤️ for music compliance and AI-powered analysis**
