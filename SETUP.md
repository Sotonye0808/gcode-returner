# GCode Returner API - Setup Instructions

This guide provides step-by-step instructions for setting up and running the GCode Returner Django API.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **pip** (Python package installer - comes with Python)
- **Git** ([Download Git](https://git-scm.com/downloads))
- **Virtual environment support** (venv - comes with Python)

### Verify Prerequisites

Open a command prompt/terminal and run:

```bash
python --version    # Should show Python 3.8+
pip --version       # Should show pip version
git --version       # Should show git version
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Sotonye0808/gcode-returner.git
cd gcode-returner
```

### 2. Create and Activate Virtual Environment

**On Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your command prompt, indicating the virtual environment is active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- Django 4.2.7
- Django REST Framework
- Django CORS Headers
- OpenCV Python
- NumPy
- scikit-image
- Pillow
- python-dotenv

### 4. Configure Environment Variables

Copy the example environment file:

**On Windows:**

```cmd
copy .env.example .env
```

**On macOS/Linux:**

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred text editor and update the paths:

```env
# Update this path to match your project location
COMMON_DIR=C:\Users\YourUsername\path\to\gcode-returner

# Generate a secure secret key for production
SECRET_KEY=your-secure-secret-key-here

# Set to False in production
DEBUG=True

# Add your domain names for production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Add your frontend URLs
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

This creates the SQLite database and applies any necessary migrations.

### 6. Create Required Directories

The following directories will be created automatically if they don't exist:

- `media/` - For uploaded files
- `logs/` - For application logs
- `testing_images/` - For test images (gitignored)
- `gcode_experiments/` - For G-code outputs (gitignored)

### 7. Test the Installation

Start the development server:

```bash
python manage.py runserver
```

You should see output like:

```
System check identified no issues (0 silenced).
January 01, 2024 - 12:00:00
Django version 4.2.7, using settings 'gcode_returner.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 8. Verify API is Working

Open a new terminal/command prompt and run:

```bash
python test_api.py
```

Or test manually with curl:

```bash
curl http://localhost:8000/api/health/
```

Expected response:

```json
{
  "status": "healthy",
  "service": "GCode Returner API",
  "version": "1.0.0",
  "endpoints": {
    "convert": "/api/convert/",
    "ssim": "/api/evaluate/ssim/",
    "smoothness": "/api/evaluate/smoothness/",
    "execution_error": "/api/evaluate/execution-error/"
  }
}
```

## Quick Start Scripts

For convenience, you can use the provided startup scripts:

**On Windows:**

```cmd
start_server.bat
```

**On macOS/Linux:**

```bash
chmod +x start_server.sh
./start_server.sh
```

These scripts will:

1. Create virtual environment if it doesn't exist
2. Activate virtual environment
3. Install dependencies
4. Create .env file from template if needed
5. Run migrations
6. Start the development server

## API Usage Examples

### 1. Convert SVG to G-code

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{"svg_data": "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\" stroke=\"black\" fill=\"none\"/></svg>"}'
```

### 2. Calculate SSIM (using test images)

First, make sure you have test images in the `testing_images/` directory, then:

```bash
curl -X POST http://localhost:8000/api/evaluate/ssim/ \
  -F "original_image=@testing_images/image1.jpg" \
  -F "reproduced_image=@testing_images/image2.jpg"
```

### 3. Calculate Line Smoothness

```bash
curl -X POST http://localhost:8000/api/evaluate/smoothness/ \
  -F "image=@testing_images/signature.jpg"
```

### 4. Calculate Execution Error

```bash
curl -X POST http://localhost:8000/api/evaluate/execution-error/ \
  -H "Content-Type: application/json" \
  -d '{"expected_toolpath": [[10,20],[15,25],[20,30]], "actual_toolpath": [[10,21],[14,26],[19,31]]}'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors

**Solution:** Make sure your virtual environment is activated and dependencies are installed:

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Permission denied" errors on startup scripts

**Solution (macOS/Linux):** Make the script executable:

```bash
chmod +x start_server.sh
```

#### 3. "Port already in use" error

**Solution:** Either stop the process using port 8000 or use a different port:

```bash
python manage.py runserver 8080
```

#### 4. Environment variable not found

**Solution:** Make sure the `.env` file exists and contains the correct variables:

```bash
# Check if .env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# If it doesn't exist, copy from template
cp .env.example .env     # macOS/Linux
copy .env.example .env   # Windows
```

#### 5. Image processing errors

**Solution:** Make sure OpenCV and Pillow are properly installed:

```bash
pip uninstall opencv-python pillow
pip install opencv-python pillow
```

#### 6. Django import errors

**Solution:** Make sure Django is installed in the virtual environment:

```bash
pip install Django==4.2.7
```

### Checking Logs

If you encounter issues, check the application logs:

```bash
# View recent logs
tail -f logs/django.log  # macOS/Linux
type logs\django.log     # Windows

# Check Django server output in the terminal where you ran runserver
```

### Getting Help

1. **Check the API Documentation:** See `API_DOCUMENTATION.md` for detailed endpoint documentation
2. **Run the test script:** `python test_api.py` to verify functionality
3. **Check Django admin:** Create a superuser and access admin at `http://localhost:8000/admin/`

```bash
# Create Django superuser
python manage.py createsuperuser
```

## Development Setup

For development work:

### 1. Install Additional Development Tools

```bash
pip install black flake8 isort pytest-django
```

### 2. Code Formatting

```bash
# Format code
black .

# Check code style
flake8 .

# Sort imports
isort .
```

### 3. Running Tests

```bash
# Run Django tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Production Deployment Notes

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Use a production database (PostgreSQL/MySQL)
3. Configure proper static file serving
4. Use a production WSGI server (gunicorn, uWSGI)
5. Set up proper logging and monitoring
6. Configure HTTPS and security headers
7. Use environment-specific settings

Example production settings in `.env`:

```env
DEBUG=False
SECRET_KEY=your-very-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/gcode_db
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

## Next Steps

After successful setup:

1. **Explore the API:** Use the provided examples or API documentation
2. **Integrate with your frontend:** Use the CORS-enabled endpoints
3. **Customize configuration:** Modify G-code settings in `py_svg2gcode/config.py`
4. **Add authentication:** Implement user authentication if needed
5. **Monitor performance:** Set up logging and monitoring for production use

For detailed API usage, see the `API_DOCUMENTATION.md` file.
For project overview and features, see the main `README.md` file.
