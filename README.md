# GCode Returner API - Django Backend

A comprehensive Django REST API for SVG to G-code conversion and signature evaluation metrics. This backend service provides robust endpoints for CNC/3D printing workflows and signature analysis applications.

## 🚀 Features

### Core Functionality

- **SVG to G-code Conversion**: Convert SVG files or raw SVG data to G-code for CNC machines and 3D printers
- **Signature Evaluation Metrics**:
  - **SSIM (Structural Similarity Index)**: Compare two images for perceptual similarity
  - **Line Smoothness Analysis**: Evaluate the smoothness and consistency of signature strokes
  - **G-code Execution Error**: Measure accuracy of robot/CNC execution against expected toolpaths

### API Features

- RESTful API design with comprehensive documentation
- Support for file uploads and base64 encoded data
- Robust input validation and error handling
- CORS support for frontend integration
- Health check endpoint for monitoring
- Comprehensive logging and monitoring

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🛠 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sotonye0808/gcode-returner.git
cd gcode-returner
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database (optional, defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Common Directory (for compatibility with existing modules)
COMMON_DIR=c:\Users\Sotonye\OneDrive\Documents\school work\Final year project related\gcode-returner
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

## 🚀 Quick Start

### Start the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Health Check

Test the API is running:

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

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/
```

### Authentication

Currently, the API is open and doesn't require authentication. Authentication can be added as needed.

### Endpoints Overview

| Endpoint                     | Method | Description                      |
| ---------------------------- | ------ | -------------------------------- |
| `/convert/`                  | POST   | Convert SVG to G-code            |
| `/evaluate/ssim/`            | POST   | Calculate SSIM between images    |
| `/evaluate/smoothness/`      | POST   | Calculate line smoothness score  |
| `/evaluate/execution-error/` | POST   | Calculate G-code execution error |
| `/health/`                   | GET    | API health check                 |

## 💡 Usage Examples

### 1. SVG to G-code Conversion

#### Using Raw SVG Data

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{
    "svg_data": "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\" fill=\"none\" stroke=\"black\"/></svg>"
  }'
```

#### Using File Upload

```bash
curl -X POST http://localhost:8000/api/convert/ \
  -F "svg_file=@path/to/your/file.svg"
```

#### Response

```json
{
  "success": true,
  "gcode": "G28\nG1 Z0.0\nM05\n...",
  "message": "SVG converted successfully to G-code",
  "metadata": {
    "gcode_lines": 150,
    "gcode_size": 2048
  }
}
```

### 2. SSIM Evaluation

#### Using File Upload

```bash
curl -X POST http://localhost:8000/api/evaluate/ssim/ \
  -F "original_image=@original.jpg" \
  -F "reproduced_image=@reproduced.jpg"
```

#### Using Base64 Data

```bash
curl -X POST http://localhost:8000/api/evaluate/ssim/ \
  -H "Content-Type: application/json" \
  -d '{
    "original_image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA...",
    "reproduced_image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
  }'
```

#### Response

```json
{
  "success": true,
  "ssim_score": 0.8542,
  "similarity_percentage": 85.42,
  "message": "SSIM calculated successfully"
}
```

### 3. Line Smoothness Evaluation

```bash
curl -X POST http://localhost:8000/api/evaluate/smoothness/ \
  -F "image=@signature.jpg"
```

#### Response

```json
{
  "success": true,
  "smoothness_score": 0.7823,
  "smoothness_percentage": 78.23,
  "quality_rating": "Good",
  "message": "Line smoothness calculated successfully"
}
```

### 4. G-code Execution Error

```bash
curl -X POST http://localhost:8000/api/evaluate/execution-error/ \
  -H "Content-Type: application/json" \
  -d '{
    "expected_toolpath": [[10, 20], [15, 25], [20, 30]],
    "actual_toolpath": [[10, 21], [14, 26], [19, 31]]
  }'
```

#### Response

```json
{
  "success": true,
  "mean_error": 1.247,
  "individual_errors": [1.0, 1.414, 1.414],
  "max_error": 1.414,
  "min_error": 1.0,
  "accuracy_percentage": 87.53,
  "message": "Execution error calculated successfully"
}
```

## 📁 Project Structure

```
gcode-returner/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── .gitignore              # Git ignore rules
│
├── gcode_returner/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django configuration
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
│
├── gcode_api/               # Main API application
│   ├── __init__.py
│   ├── apps.py             # App configuration
│   ├── models.py           # Database models (currently empty)
│   ├── serializers.py      # DRF serializers for validation
│   ├── services.py         # Business logic layer
│   ├── views.py            # API views/endpoints
│   ├── urls.py             # API URL patterns
│   ├── admin.py            # Django admin configuration
│   └── tests.py            # Test cases
│
├── py_svg2gcode/            # SVG to G-code conversion library
│   ├── __init__.py
│   ├── svg2gcode.py        # Main conversion class
│   ├── config.py           # Configuration settings
│   └── local_lib/          # Supporting libraries
│
├── evaluation_modules/      # Evaluation metric modules
│   ├── ssim.py             # SSIM calculation
│   ├── line_smoothness.py  # Line smoothness analysis
│   └── gcode_error.py      # Execution error calculation
│
├── testing_images/          # Test image directory (gitignored)
├── gcode_experiments/       # G-code output directory (gitignored)
└── logs/                   # Application logs
```

## ⚙️ Configuration

### Environment Variables

| Variable               | Description                | Default                 |
| ---------------------- | -------------------------- | ----------------------- |
| `SECRET_KEY`           | Django secret key          | Required                |
| `DEBUG`                | Debug mode                 | `False`                 |
| `ALLOWED_HOSTS`        | Allowed host names         | `localhost,127.0.0.1`   |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins       | `http://localhost:3000` |
| `DATABASE_URL`         | Database connection string | SQLite                  |

### G-code Configuration

The G-code generation can be configured in `py_svg2gcode/config.py`:

```python
# Print bed dimensions (mm)
bed_max_x = 150
bed_max_y = 150

# Curve smoothness (smaller = smoother)
smoothness = 0.2

# G-code templates
preamble = "G28\nG1 Z0.0\nM05"
postamble = "G28"
```

## 🧪 Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt

# Run development server with auto-reload
python manage.py runserver
```

### Code Style and Linting

```bash
# Install development tools
pip install black flake8 isort

# Format code
black .

# Check code style
flake8 .

# Sort imports
isort .
```

### Creating Migrations (if models are added)

```bash
python manage.py makemigrations gcode_api
python manage.py migrate
```

### Creating Admin User

```bash
python manage.py createsuperuser
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test gcode_api

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

### Manual API Testing

Use the provided examples above or tools like:

- **Postman**: Import the API collection (can be generated)
- **curl**: Command-line testing (examples provided)
- **HTTPie**: User-friendly HTTP client
- **Insomnia**: REST client

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in environment variables
2. Configure proper `SECRET_KEY`
3. Set up proper database (PostgreSQL recommended)
4. Configure static file serving
5. Set up proper logging

### Using Docker (Optional)

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Environment-Specific Configuration

- **Development**: Use SQLite, DEBUG=True
- **Staging**: Use PostgreSQL, DEBUG=False, limited CORS
- **Production**: Use PostgreSQL, DEBUG=False, strict security settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`python manage.py test`)
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Write tests for new functionality
- Update documentation as needed
- Ensure backward compatibility

## 📄 License

This project is part of a final year academic project. Please contact the author for usage permissions.

## 📞 Contact

**Author**: Sotonye Dagogo  
**Email**: sotydagz@gmail.com  
**GitHub**: [@Sotonye0808](https://github.com/Sotonye0808)

## 🙏 Acknowledgments

- Original SVG to G-code conversion based on [pjpscriv/py-svg2gcode](https://github.com/pjpscriv/py-svg2gcode)
- SSIM implementation using scikit-image
- Line smoothness analysis using OpenCV
- Django REST Framework for API development

---

For detailed API documentation and examples, visit the health check endpoint after starting the server.
