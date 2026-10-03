# Quick Start Guide

Get the Flask application up and running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Setup Steps

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work for development).

### 4. Run the Application

```bash
python run.py
```

The application will start at `http://localhost:5000`

### 5. Test the Application

Open your browser and visit:

- `http://localhost:5000/` - Root endpoint
- `http://localhost:5000/health` - Health check

Or run the test suite:

```bash
pytest
```

## What's Next?

- Check out the [README.md](README.md) for detailed documentation
- Review the project structure in `app/`
- Start implementing features according to the tasks

## Troubleshooting

### Virtual Environment Issues

If `source venv/bin/activate` doesn't work:

**Windows:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

### Port Already in Use

If port 5000 is already in use, set a different port:

```bash
export PORT=8000
python run.py
```

### Database Issues

If you encounter database errors, delete the database and restart:

```bash
rm instance/dev.db
python run.py
```

## Need Help?

Check the [README.md](README.md) for more detailed information.

````