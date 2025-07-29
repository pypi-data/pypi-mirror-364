# FastAPI Colorful Logging Middleware 
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A beautiful, colorful HTTP request logging middleware for FastAPI applications that provides Go-style formatted logs. The middleware automatically captures and logs detailed information about each incoming request, including timing, client IP, HTTP method, and response status with color-coded output.

The middleware extracts client IP addresses from various sources including direct client connection, `X-Forwarded-For`, and `X-Real-IP` headers by default. Request duration is automatically calculated and displayed in the most appropriate unit (microseconds, milliseconds, or seconds) for optimal readability.

## Installation

Install the package using pip:

```bash
pip install fastapi-logging-middleware
```

## Quick Start

### Method 1: Using add_middleware (Recommended)

```python
from fastapi import FastAPI
from logging_middleware import GoStyleLoggingMiddleware

app = FastAPI()

# Add the middleware
app.add_middleware(GoStyleLoggingMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Method 2: Using middleware parameter in FastAPI

```python
from fastapi import FastAPI
from starlette.middleware import Middleware
from logging_middleware import GoStyleLoggingMiddleware

# Add middleware during app creation
app = FastAPI(
    middleware=[
        Middleware(GoStyleLoggingMiddleware)
    ]
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```


## Example Output
![Example Output](images/img.png)

## Log Format

The middleware outputs logs in the following format:

```
YYYY-MM-DD HH:MM:SS.ffffff [STATUS] | DURATION | CLIENT_IP | [METHOD] "PATH?QUERY"
```

## Color Coding

- **Status Codes:**
  - 2xx: Green background
  - 3xx: Yellow background  
  - 4xx: Red background
  - 5xx: Magenta background

- **HTTP Methods:**
  - GET: Blue background
  - POST: Green background
  - PUT: Yellow background
  - DELETE: Red background
  - PATCH: Cyan background
  - HEAD: Magenta background
  - OPTIONS: White background

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

