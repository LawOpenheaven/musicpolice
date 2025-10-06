# 🛠️ Development Setup Guide

This guide will help you set up the Music Police application for development.

## 📋 Prerequisites

### Required Software

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download here](https://www.postgresql.org/download/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **Node.js 16+** (optional) - [Download here](https://nodejs.org/)

### Recommended Tools

- **VS Code** or **PyCharm** - Code editor
- **pgAdmin** - PostgreSQL administration tool
- **Postman** - API testing

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/musicpolice.git
cd musicpolice
```

### 2. Set Up Python Environment

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

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb musicpolice_db

# Or using psql:
psql -U postgres
CREATE DATABASE musicpolice_db;
\q
```

### 4. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your database credentials
# Example .env content:
DATABASE_URL=postgresql://username:password@localhost:5432/musicpolice_db
```

### 5. Initialize Database

```bash
# This creates all tables and default data
python database_init.py
```

### 6. Run the Application

```bash
# Start the development server
python -m app.main

# Or with auto-reload for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access the Application

Open your browser and go to: `http://localhost:8000`

## 🔧 Development Workflow

### Code Structure

```
app/
├── api/           # API routes and endpoints
├── core/          # Core configuration
├── db/            # Database models and session
├── services/      # Business logic
└── workers/       # Background tasks

static/            # Frontend assets
templates/         # HTML templates
migrations/        # Database migrations
```

### Making Changes

1. **Backend Changes**

   - Edit files in `app/` directory
   - Server auto-reloads with `--reload` flag
   - Test API endpoints at `http://localhost:8000/docs`

2. **Frontend Changes**

   - Edit files in `static/` and `templates/`
   - Refresh browser to see changes
   - Use browser dev tools for debugging

3. **Database Changes**
   - Create migrations: `alembic revision --autogenerate -m "Description"`
   - Apply migrations: `alembic upgrade head`

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest test_api.py

# Run with coverage
pytest --cov=app
```

## 🐛 Common Issues

### Database Connection Issues

- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `psql -l`

### Python Import Issues

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python path: `python -c "import sys; print(sys.path)"`

### Port Already in Use

- Change port: `uvicorn app.main:app --port 8001`
- Kill existing process: `lsof -ti:8000 | xargs kill`

## 📚 Useful Commands

### Database

```bash
# Connect to database
psql -U username -d musicpolice_db

# View tables
\dt

# View table structure
\d table_name

# Reset database (careful!)
dropdb musicpolice_db && createdb musicpolice_db
python database_init.py
```

### Development

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

### Git

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push changes
git push origin branch-name
```

## 🔍 Debugging

### Backend Debugging

- Check server logs in terminal
- Use `print()` statements for debugging
- Set breakpoints in VS Code/PyCharm
- Check API docs at `http://localhost:8000/docs`

### Frontend Debugging

- Use browser developer tools (F12)
- Check console for JavaScript errors
- Use `console.log()` for debugging
- Check network tab for API calls

### Database Debugging

- Use pgAdmin for visual database inspection
- Check database logs
- Use SQL queries to inspect data

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## 📚 Available Documentation

This repository includes minimal documentation to keep it clean:

- `README_GITHUB.md` - Main project overview and setup
- `DEVELOPMENT_SETUP.md` - This development guide
- `LICENSE` - MIT License

## 🤝 Getting Help

1. Check this guide first
2. Look at existing issues on GitHub
3. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Error messages
   - Your environment details

## 🎯 Next Steps

Once you have the application running:

1. Explore the dashboard at `http://localhost:8000`
2. Try uploading an audio file
3. Check the API documentation at `http://localhost:8000/docs`
4. Look at the code structure in the `app/` directory
5. Start making your changes!

Happy coding! 🎵✨
