# GCode Returner API Documentation

## Overview

The GCode Returner API is a RESTful web service that provides SVG to G-code conversion, signature evaluation capabilities, and a playground database for testing and data collection. Built with Django REST Framework, it offers robust, scalable endpoints for CNC/3D printing workflows and signature analysis applications.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API provides two types of access:

### 1. Open Access
Standard API endpoints that accept requests from any host and return their output without authentication.

### 2. Signed Requests
Special endpoints that only accept requests from trusted frontend origins with HMAC signature verification. These endpoints can store and modify database records.

## Response Format

All API responses follow a consistent JSON format:

### Success Response

```json
{
    "success": true,
    "data": {...},
    "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error message"
}
```

## Rate Limiting

- **Rate Limit**: 100 requests per hour per IP address
- **Headers**: Rate limit information is included in response headers

## Open Access Endpoints

These endpoints accept requests from any host and do not require authentication.

### 1. Health Check

**GET** `/health/`

Check API service status and get endpoint information.

**Response:**

```json
{
  "status": "healthy",
  "service": "GCode Returner API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
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

---

### 2. SVG to G-code Conversion

**POST** `/convert/`

Convert SVG data to G-code for CNC machines or 3D printers.

**Content-Type:** `application/json` OR `multipart/form-data`

#### Request Options

##### Option 1: Raw SVG Data (JSON)

```json
{
  "svg_data": "<svg width=\"100\" height=\"100\" xmlns=\"http://www.w3.org/2000/svg\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\" fill=\"none\" stroke=\"black\"/></svg>"
}
```

##### Option 2: File Upload (Form Data)

```
Content-Type: multipart/form-data
svg_file: [file.svg]
```

#### Response

```json
{
  "success": true,
  "gcode": "G28\nG1 Z0.0\nM05\nG0 X10.0 Y90.0\nM03\nG1 X90.0 Y90.0\n...",
  "message": "SVG converted successfully to G-code",
  "metadata": {
    "gcode_lines": 150,
    "gcode_size": 2048
  }
}
```

#### Error Responses

- **400 Bad Request**: Invalid SVG data or format
- **413 Payload Too Large**: File size exceeds limit (10MB)
- **500 Internal Server Error**: Conversion processing error

---

### 3. SSIM Evaluation

**POST** `/evaluate/ssim/`

Calculate Structural Similarity Index (SSIM) between two images.

**Content-Type:** `application/json` OR `multipart/form-data`

#### Request Options

##### Option 1: File Upload (Form Data)

```
Content-Type: multipart/form-data
original_image: [file.jpg/png]
reproduced_image: [file.jpg/png]
```

##### Option 2: Base64 Data (JSON)

```json
{
  "original_image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA...",
  "reproduced_image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
}
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

#### SSIM Score Interpretation

- `1.0`: Perfect match (identical images)
- `> 0.9`: Excellent similarity
- `> 0.7`: Good similarity
- `> 0.5`: Moderate similarity
- `< 0.5`: Poor similarity

---

### 4. Line Smoothness Evaluation

**POST** `/evaluate/smoothness/`

Analyze line smoothness and consistency in signature images.

**Content-Type:** `application/json` OR `multipart/form-data`

#### Request Options

##### Option 1: File Upload (Form Data)

```
Content-Type: multipart/form-data
image: [file.jpg/png]
```

##### Option 2: Base64 Data (JSON)

```json
{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
}
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

#### Quality Ratings

- `Excellent`: Score ≥ 0.8
- `Good`: Score ≥ 0.6
- `Fair`: Score ≥ 0.4
- `Poor`: Score < 0.4

---

### 5. G-code Execution Error

**POST** `/evaluate/execution-error/`

Calculate execution error between expected and actual toolpaths.

**Content-Type:** `application/json`

#### Request

```json
{
  "expected_toolpath": [
    [10.0, 20.0],
    [15.0, 25.0],
    [20.0, 30.0],
    [25.0, 35.0]
  ],
  "actual_toolpath": [
    [10.0, 21.0],
    [14.0, 26.0],
    [19.0, 31.0],
    [26.0, 34.0]
  ]
}
```

#### Response

```json
{
  "success": true,
  "mean_error": 1.247,
  "individual_errors": [1.0, 1.414, 1.414, 1.414],
  "max_error": 1.414,
  "min_error": 1.0,
  "error_std": 0.239,
  "accuracy_percentage": 87.53,
  "message": "Execution error calculated successfully"
}
```

---

## Signed Request Endpoints

These endpoints require HMAC signature verification and only accept requests from trusted frontend origins.

### Trusted Origins

The following origins are currently trusted:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:4200`
- `http://127.0.0.1:4200`

### HMAC Signature Generation

To generate a valid HMAC signature:

1. Create a canonical string from your request data (excluding the signature field)
2. Sort the data keys alphabetically
3. Create a string in format: `key1=value1&key2=value2&...`
4. Generate HMAC-SHA256 signature using the shared signing key

Example in JavaScript:
```javascript
const crypto = require('crypto');

function generateSignature(data, signingKey) {
    // Remove signature field from data
    const cleanData = { ...data };
    delete cleanData.request_signature;
    
    // Create canonical string
    const sortedKeys = Object.keys(cleanData).sort();
    const canonicalString = sortedKeys
        .map(key => `${key}=${cleanData[key]}`)
        .join('&');
    
    // Generate HMAC signature
    return crypto
        .createHmac('sha256', signingKey)
        .update(canonicalString)
        .digest('hex');
}
```

### 6. Signed Data Submission

**POST** `/signed/submit/`

Submit user data and signature for storage in the playground database.

**Authentication:** HMAC signature verification required

**Content-Type:** `application/json`

#### Request Format

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student",
  "department": "Computer Science",
  "faculty": "Engineering",
  "submitted_at": "2024-01-01T12:00:00Z",
  "svg_data": "<svg width=\"100\" height=\"100\">...</svg>",
  "request_signature": "hmac_sha256_signature_here"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | User's full name |
| email | string | Yes | User's email (unique identifier) |
| role | string | No | User's role (student, staff, lecturer, hod, dean, researcher, visitor, other) |
| department | string | No | User's department |
| faculty | string | No | User's faculty |
| submitted_at | datetime | No | Submission timestamp (ISO format) |
| svg_data | string | Yes | SVG signature data |
| request_signature | string | Yes | HMAC signature for verification |

#### Response

```json
{
  "success": true,
  "user_id": 123,
  "signature_id": 456,
  "message": "Data stored successfully",
  "gcode_preview": "G28\nG1 Z0.0\nM05\n...",
  "metadata": {
    "gcode_lines": 150,
    "gcode_size": 2048,
    "movement_commands": 120,
    "setup_commands": 30,
    "estimated_duration": "15.0 seconds"
  }
}
```

#### User Data Behavior

- If a user with the given email exists, their data will be updated with new information
- If the user doesn't exist, a new user record will be created
- Each submission creates a new signature record, allowing multiple signatures per user
- The `submitted_at` field is only set for new users (not updated for existing users)

### 7. User Data Retrieval

**POST** `/signed/retrieve/`

Retrieve all data for a user by email address.

**Authentication:** HMAC signature verification required

**Content-Type:** `application/json`

#### Request Format

```json
{
  "email": "john.doe@example.com",
  "request_signature": "hmac_sha256_signature_here"
}
```

#### Response

```json
{
  "success": true,
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student",
    "department": "Computer Science",
    "faculty": "Engineering",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "submitted_at": "2024-01-01T12:00:00Z"
  },
  "signatures": [
    {
      "id": 456,
      "svg_data": "<svg>...</svg>",
      "gcode_data": "G28\nG1 Z0.0\nM05\n...",
      "metadata": {
        "gcode_lines": 150,
        "gcode_size": 2048,
        "movement_commands": 120,
        "setup_commands": 30,
        "estimated_duration": "15.0 seconds"
      },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad Request - Invalid input data |
| 403 | Forbidden - Signature verification failed or untrusted origin |
| 404 | Not Found - User not found |
| 413 | Payload Too Large - File size exceeds limit |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server processing error |

## File Upload Limitations

- **Maximum file size**: 10MB
- **Supported image formats**: PNG, JPG, JPEG
- **Supported SVG**: Valid XML-based SVG files
- **Base64 encoding**: Supported with or without data URL prefix

## Database Schema

### User Model

```json
{
  "id": "integer (auto-generated)",
  "name": "string (max 255 chars)",
  "email": "string (unique)",
  "role": "string (choices: student, staff, lecturer, hod, dean, researcher, visitor, other)",
  "department": "string (optional, max 255 chars)",
  "faculty": "string (optional, max 255 chars)",
  "created_at": "datetime (auto-generated)",
  "updated_at": "datetime (auto-updated)",
  "submitted_at": "datetime (set on first submission)"
}
```

### SignatureData Model

```json
{
  "id": "integer (auto-generated)",
  "user": "foreign key to User",
  "svg_data": "text",
  "gcode_data": "text",
  "gcode_metadata": "json object",
  "created_at": "datetime (auto-generated)"
}
```

## Usage Examples

### Python Example

```python
import requests
import base64

# Health check
response = requests.get('http://localhost:8000/api/health/')
print(response.json())

# SVG to G-code conversion
svg_data = '<svg width="100" height="100"><rect x="10" y="10" width="80" height="80"/></svg>'
response = requests.post('http://localhost:8000/api/convert/',
                        json={'svg_data': svg_data})
gcode = response.json()['gcode']

# SSIM evaluation with files
with open('original.jpg', 'rb') as f1, open('reproduced.jpg', 'rb') as f2:
    files = {'original_image': f1, 'reproduced_image': f2}
    response = requests.post('http://localhost:8000/api/evaluate/ssim/', files=files)
    ssim_score = response.json()['ssim_score']
```

### JavaScript Example

```javascript
// SVG to G-code conversion
const svgData =
  '<svg width="100" height="100"><rect x="10" y="10" width="80" height="80"/></svg>';

fetch("http://localhost:8000/api/convert/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ svg_data: svgData }),
})
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      console.log("G-code:", data.gcode);
    }
  });

// File upload for SSIM
const formData = new FormData();
formData.append("original_image", originalFile);
formData.append("reproduced_image", reproducedFile);

fetch("http://localhost:8000/api/evaluate/ssim/", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => {
    console.log("SSIM Score:", data.ssim_score);
  });
```

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:8000/api/health/

# SVG conversion
curl -X POST http://localhost:8000/api/convert/ \
  -H "Content-Type: application/json" \
  -d '{"svg_data": "<svg width=\"100\" height=\"100\"><rect x=\"10\" y=\"10\" width=\"80\" height=\"80\"/></svg>"}'

# File upload for SSIM
curl -X POST http://localhost:8000/api/evaluate/ssim/ \
  -F "original_image=@original.jpg" \
  -F "reproduced_image=@reproduced.jpg"

# Execution error calculation
curl -X POST http://localhost:8000/api/evaluate/execution-error/ \
  -H "Content-Type: application/json" \
  -d '{"expected_toolpath": [[10,20],[15,25]], "actual_toolpath": [[10,21],[14,26]]}'
```

## Integration Notes

### Frontend Integration

- Use appropriate CORS settings for your frontend domain
- Handle file uploads with proper form data encoding
- Implement proper error handling for all status codes
- Consider implementing retry logic for rate-limited requests

### Backend Integration

- The API is stateless and can be easily scaled horizontally
- All endpoints return consistent JSON responses
- File processing is done in memory with automatic cleanup
- Consider implementing authentication for production use

### Performance Considerations

- Image processing can be CPU-intensive for large files
- SVG conversion time depends on complexity
- Consider implementing caching for repeated requests
- Monitor memory usage with large file uploads

## Security Considerations

1. **HMAC Signatures**: All signed requests must include valid HMAC signatures
2. **Origin Verification**: Requests are verified against trusted frontend origins
3. **Data Validation**: All input data is validated before processing
4. **Rate Limiting**: API calls are rate-limited to prevent abuse
5. **Logging**: All requests and errors are logged for monitoring

## Development and Testing

For development and testing:

1. **Signing Key**: Use the development signing key or set `FRONTEND_SIGNING_KEY` environment variable
2. **Trusted Origins**: Localhost origins are trusted by default for development
3. **Database**: Uses SQLite for development, can be configured for production databases
4. **Playground Data**: All data in the playground database is for testing purposes

For additional support or questions, please refer to the main README.md file or contact the development team.
