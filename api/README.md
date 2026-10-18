# Learning S3 with FastAPI

This repository demonstrates how to integrate Amazon S3 storage with a FastAPI application.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview
This project shows a simple FastAPI service that provides CRUD operations for interacting with files stored in an Amazon S3 bucket. It includes authentication, file upload/download, and listing capabilities.

## Prerequisites
- Python 3.10+
- AWS account with an S3 bucket
- AWS credentials configured (via environment variables or AWS CLI)
- FastAPI and Uvicorn installed

## Installation
```bash
git clone https://github.com/yourrepo/learning-s3-with-fastapi.git
cd learning-s3-with-fastapi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Create a `.env` file in the root directory with the following variables:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

## Running the App
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/files/` | Upload a file to S3 |
| `GET` | `/files/{file_id}` | Download a file from S3 |
| `DELETE` | `/files/{file_id}` | Delete a file from S3 |
| `GET` | `/files/` | List all files in the bucket |

## Testing
Run the test suite with:
```bash
pytest
```

## Contributing
Feel free to open issues or pull requests.

## License
This project is licensed under the MIT License.