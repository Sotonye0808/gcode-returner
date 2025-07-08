# GCode Returner API - Django Backend

A comprehensive Django REST API for SVG to G-code conversion, signature evaluation metrics, and a playground database for testing and data collection. Built with Django REST Framework, this backend service provides robust endpoints for CNC/3D printing workflows and signature analysis applications with secure data storage capabilities.

## 🚀 Features

### Core Functionality

- **SVG to G-code Conversion**: Convert SVG files or raw SVG data to G-code for CNC machines and 3D printers
- **Signature Evaluation Metrics**:
  - **SSIM (Structural Similarity Index)**: Compare two images for perceptual similarity
  - **Line Smoothness Analysis**: Evaluate the smoothness and consistency of signature strokes
  - **G-code Execution Error**: Measure accuracy of robot/CNC execution against expected toolpaths

### API Features

- **Open Access Endpoints**: Standard API endpoints that accept requests from any host
- **Signed Request Endpoints**: Special endpoints for trusted frontend origins with HMAC signature verification
- **Playground Database**: Store and retrieve user data and signatures for testing and data collection
- **Robust Input Validation**: Comprehensive error handling and data validation
- **CORS Support**: Proper CORS configuration for frontend integration
- **Health Check Endpoint**: Monitor API status and endpoints
- **Comprehensive Logging**: Detailed logging and monitoring capabilities

### Database Features

- **User Management**: Store user information (name, email, role, department, faculty)
- **Signature Storage**: Store SVG data and generated G-code for each user
- **Data Retrieval**: Retrieve all user data and signatures by email
- **Update Capability**: Update existing user data while preserving signature history
- **HMAC Security**: Secure signed requests with HMAC-SHA256 verification

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Database Schema](#database-schema)
- [Frontend Integration](#frontend-integration)
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

# Frontend Signing Key for HMAC verification
FRONTEND_SIGNING_KEY=your-signing-key-for-hmac-verification

# Trusted Frontend Origins
TRUSTED_FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200

# Common Directory (for compatibility with existing modules)
COMMON_DIR=c:\Users\Sotonye\OneDrive\Documents\school work\Final year project related\gcode-returner
```

### Step 5: Run Database Migrations

```bash
python manage.py makemigrations
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

Expected response includes all available endpoints:

```json
{
  "status": "healthy",
  "service": "GCode Returner API",
  "version": "1.0.0",
  "endpoints": {
    "convert": "/api/convert/",
    "ssim": "/api/evaluate/ssim/",
    "smoothness": "/api/evaluate/smoothness/",
    "execution_error": "/api/evaluate/execution-error/",
    "signed_submit": "/api/signed/submit/",
    "signed_retrieve": "/api/signed/retrieve/"
  }
}
```

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/
```

### Endpoint Categories

#### 1. Open Access Endpoints

These endpoints accept requests from any host without authentication:

| Endpoint                     | Method | Description                      |
| ---------------------------- | ------ | -------------------------------- |
| `/convert/`                  | POST   | Convert SVG to G-code            |
| `/evaluate/ssim/`            | POST   | Calculate SSIM between images    |
| `/evaluate/smoothness/`      | POST   | Calculate line smoothness score  |
| `/evaluate/execution-error/` | POST   | Calculate G-code execution error |
| `/health/`                   | GET    | API health check                 |

#### 2. Signed Request Endpoints

These endpoints require HMAC signature verification from trusted origins:

| Endpoint            | Method | Description                                |
| ------------------- | ------ | ------------------------------------------ |
| `/signed/submit/`   | POST   | Submit user data and signature for storage |
| `/signed/retrieve/` | POST   | Retrieve user data by email                |

## 💡 Usage Examples

### Open Access Usage

#### SVG to G-code Conversion

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

### Signed Request Usage

#### Submit User Data with Signature

```bash
# Note: In practice, you would generate the HMAC signature programmatically
curl -X POST http://localhost:8000/api/signed/submit/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student",
    "department": "Computer Science",
    "faculty": "Engineering",
    "svg_data": "<svg>...</svg>",
    "request_signature": "calculated_hmac_signature"
  }'
```

#### Retrieve User Data

```bash
curl -X POST http://localhost:8000/api/signed/retrieve/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "email": "john.doe@example.com",
    "request_signature": "calculated_hmac_signature"
  }'
```

## 🗄️ Database Schema

### User Model

```python
{
    "id": "integer (auto-generated primary key)",
    "name": "string (max 255 characters)",
    "email": "string (unique identifier)",
    "role": "choice (student, staff, lecturer, hod, dean, researcher, visitor, other)",
    "department": "string (optional, max 255 characters)",
    "faculty": "string (optional, max 255 characters)",
    "created_at": "datetime (auto-generated)",
    "updated_at": "datetime (auto-updated)",
    "submitted_at": "datetime (set on first submission)"
}
```

### SignatureData Model

```python
{
    "id": "integer (auto-generated primary key)",
    "user": "foreign key to User model",
    "svg_data": "text field (stores SVG content)",
    "gcode_data": "text field (stores generated G-code)",
    "gcode_metadata": "JSON field (stores G-code statistics)",
    "created_at": "datetime (auto-generated)"
}
```

### Data Relationships

- One user can have multiple signature submissions
- Each signature submission stores both SVG and G-code data
- User data is updated on subsequent submissions, but signature history is preserved
- Email address serves as the unique identifier for users

## 🔧 Frontend Integration

### HMAC Signature Generation

For signed requests, generate HMAC signatures using this process:

```javascript
const crypto = require("crypto");

function generateSignature(data, signingKey) {
  // Ensure signing key is not empty
  if (!signingKey) {
    throw new Error('Signing key is required');
  }

  // Remove signature field from data
  const cleanData = { ...data };
  delete cleanData.request_signature;

  // Create canonical string (sorted keys)
  const sortedKeys = Object.keys(cleanData).sort();
  const canonicalString = sortedKeys
    .map((key) => `${key}=${cleanData[key]}`)
    .join("&");

  // Generate HMAC-SHA256 signature
  return crypto
    .createHmac("sha256", signingKey)
    .update(canonicalString)
    .digest("hex");
}
```

### Integration Example

```javascript
// Import your environment configuration
import { data } from './environment/environment';

// Submit signature data
const userData = {
  name: "John Doe",
  email: "john@example.com",
  role: "student",
  department: "Computer Science",
  svg_data: "<svg>...</svg>",
};

// Generate signature using the configured signing key
userData.request_signature = generateSignature(userData, data.gcodeReturner.signingKey);

// Send request
const response = await fetch("http://localhost:8000/api/signed/submit/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Origin: "http://localhost:3000",
  },
  body: JSON.stringify(userData),
});

const result = await response.json();
```

## 📁 Project Structure

```
gcode-returner/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── API_DOCUMENTATION.md     # Detailed API documentation
├── .gitignore              # Git ignore rules
│
├── gcode_returner/          # Django project settings
│   ├── settings.py          # Django configuration (updated)
│   ├── urls.py             # Main URL configuration
│   └── ...
│
├── gcode_api/               # Main API application
│   ├── models.py           # Database models (NEW)
│   ├── serializers.py      # DRF serializers (updated)
│   ├── services.py         # Business logic layer (updated)
│   ├── views.py            # API views/endpoints (updated)
│   ├── urls.py             # API URL patterns (updated)
│   └── ...
│
├── py_svg2gcode/            # SVG to G-code conversion library
├── evaluation_modules/      # Evaluation metric modules
├── testing_images/          # Test image directory (gitignored)
├── gcode_experiments/       # G-code output directory (gitignored)
└── logs/                   # Application logs
```

## ⚙️ Configuration

### Environment Variables

| Variable                   | Description                         | Default                      |
| -------------------------- | ----------------------------------- | ---------------------------- |
| `SECRET_KEY`               | Django secret key                   | Required                     |
| `DEBUG`                    | Debug mode                          | `False`                      |
| `ALLOWED_HOSTS`            | Allowed host names                  | `localhost,127.0.0.1`        |
| `CORS_ALLOWED_ORIGINS`     | CORS allowed origins                | `http://localhost:3000`      |
| `FRONTEND_SIGNING_KEY`     | HMAC signing key for frontend       | Required for signed requests |
| `TRUSTED_FRONTEND_ORIGINS` | Trusted origins for signed requests | `http://localhost:3000,...`  |

### Security Settings

- **HMAC Verification**: All signed requests must include valid HMAC signatures
- **Origin Checking**: Signed requests are validated against trusted origins
- **Data Validation**: All data is validated before processing
- **Rate Limiting**: API calls are rate-limited to prevent abuse
- **Input Validation**: All input data is validated before processing

## 🧪 Development

### Database Operations

```bash
# Create migrations after model changes
python manage.py makemigrations gcode_api

# Apply migrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser

# Access admin panel at http://localhost:8000/admin/
```

### Testing Signed Requests

```bash
# Run the test API script
python test_api.py

# Or test individual endpoints
curl -X POST http://localhost:8000/api/signed/submit/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"email": "test@example.com", "name": "Test User", "svg_data": "<svg></svg>", "request_signature": "test"}'
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
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set proper production values
2. **Database**: Configure PostgreSQL or MySQL for production
3. **Signing Keys**: Use secure, unique signing keys
4. **CORS Settings**: Restrict to production frontend domains
5. **Static Files**: Configure proper static file serving
6. **HTTPS**: Enable HTTPS for production

### Example Production Environment

```env
SECRET_KEY=secure-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
FRONTEND_SIGNING_KEY=secure-production-signing-key
TRUSTED_FRONTEND_ORIGINS=https://yourfrontend.com
DATABASE_URL=postgresql://user:password@localhost:5432/gcode_db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`python manage.py test`)
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

### Development Guidelines

- Follow Django best practices
- Add comprehensive tests for new features
- Update documentation for any API changes
- Ensure database migrations are included
- Test both open access and signed request functionality

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

For detailed API documentation including signed request examples and HMAC signature generation, see `API_DOCUMENTATION.md`.
