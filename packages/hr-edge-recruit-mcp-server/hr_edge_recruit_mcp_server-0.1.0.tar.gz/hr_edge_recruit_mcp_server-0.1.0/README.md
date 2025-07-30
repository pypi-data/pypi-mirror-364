# AI RecruitEdge MCP Server

A comprehensive AI-powered recruitment workflow automation server that generates interview questions, analyzes media files, and provides candidate scoring.

## Features

- **Question Generation**: AI-powered interview question generation based on job descriptions and resumes
- **Media Analysis**: Audio/video transcription and analysis for candidate evaluation
- **Candidate Scoring**: Comprehensive scoring system with technical, communication, and emotional intelligence assessment
- **Database Integration**: Full Firebase Firestore support for storing questions, analyses, and scores
- **File Management**: Complete file upload, validation, and storage system
- **Configuration Management**: Centralized configuration with environment variables
- **Health Monitoring**: Comprehensive health checks for all services

## Architecture

### Services

1. **DatabaseService**: Handles all database operations using Firebase Firestore
2. **ConfigService**: Manages application configuration and environment variables
3. **FileService**: Handles file uploads, validation, and storage
4. **AWSServices**: Manages AWS services (S3, Bedrock, Transcribe, Rekognition)
5. **PineconeService**: Manages vector store operations for similarity search

### Agents

1. **QuestionGeneratorAgent**: Generates interview questions using LLM
2. **MediaAnalyzerAgent**: Analyzes audio/video files for candidate evaluation
3. **ScoringAgent**: Provides comprehensive candidate scoring

## Required Services & Infrastructure

### 1. AWS Services

#### Amazon Bedrock
- **Purpose**: LLM inference for question generation, media analysis, and scoring
- **Models Required**: 
  - `anthropic.claude-3-sonnet-20240229-v1:0` (default)
  - `amazon.titan-embed-text-v1` (embeddings)
- **Setup**: Enable Bedrock access in AWS console, configure IAM permissions

#### Amazon S3
- **Purpose**: Media file storage and transcription output
- **Bucket**: `ai-recruitedge-media` (configurable)
- **Permissions**: Read/Write access for media files and transcriptions
- **CORS**: Configure for web uploads

#### Amazon Transcribe
- **Purpose**: Audio/video transcription for media analysis
- **Features**: Real-time and batch transcription
- **Languages**: English (en-US) by default
- **Output**: JSON format to S3

#### Amazon Rekognition
- **Purpose**: Emotion analysis in video files
- **Features**: Face detection and emotion analysis
- **Permissions**: Access to S3 bucket for video analysis

#### AWS IAM Configuration
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ai-recruitedge-media",
                "arn:aws:s3:::ai-recruitedge-media/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:ListTranscriptionJobs"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectFaces",
                "rekognition:DetectLabels"
            ],
            "Resource": "*"
        }
    ]
}
```

### 2. Database Services

#### Firebase Firestore (Production)
- **Purpose**: NoSQL database for all application data
- **Collections**: `questions`, `media_analyses`, `candidate_scores`, `interview_sessions`
- **Features**: Real-time updates, automatic scaling, offline support
- **Security**: Row-level security rules
- **Backup**: Automated daily backups

#### Firebase Emulator (Development)
- **Purpose**: Local development database
- **Setup**: Firebase emulator suite
- **Features**: Local testing without Firebase costs

### 3. Vector Database

#### Pinecone
- **Purpose**: Vector similarity search for question context
- **Index**: `recruitedge-questions` (configurable)
- **Dimensions**: 1536 (Titan embedding dimension)
- **Metric**: Cosine similarity
- **Environment**: Production environment

### 4. File Storage

#### Local Storage
- **Upload Directory**: `./uploads` (configurable)
- **Temp Directory**: `./temp` (configurable)
- **Permissions**: Read/Write access
- **Cleanup**: Automated cleanup of old files

#### S3 Storage (Production)
- **Bucket**: `ai-recruitedge-media`
- **CORS Configuration**:
```json
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": []
        }
    ]
}
```

### 5. Application Infrastructure

#### Web Server
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000 (configurable)
- **Host**: 0.0.0.0 (configurable)
- **SSL**: HTTPS in production

#### Load Balancer (Production)
- **Type**: Application Load Balancer (AWS ALB)
- **Health Checks**: `/health` endpoint
- **SSL Termination**: Configure SSL certificate
- **Auto Scaling**: Based on CPU/memory usage

#### Monitoring & Logging
- **Application Logs**: Structured JSON logging
- **Metrics**: Prometheus metrics endpoint
- **Health Checks**: Comprehensive service health monitoring
- **Alerting**: CloudWatch alarms for critical metrics

## Installation & Setup

### 1. Prerequisites

#### System Requirements
- **Python**: 3.9+
- **Memory**: 4GB+ RAM
- **Storage**: 50GB+ for media files
- **CPU**: 2+ cores recommended

#### Operating System
- **Linux**: Ubuntu 20.04+ (recommended)
- **Windows**: Windows 10+ (development)
- **macOS**: 10.15+ (development)

### 2. Environment Setup

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. AWS Setup

#### Install AWS CLI
```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# macOS
brew install awscli

# Windows
# Download from AWS website
```

#### Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
```

#### Create S3 Bucket
```bash
aws s3 mb s3://ai-recruitedge-media
aws s3api put-bucket-cors --bucket ai-recruitedge-media --cors-configuration file://cors.json
```

### 4. Firebase Setup

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Enable Firestore Database
4. Set up security rules

#### Install Firebase CLI
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init firestore
```

#### Configure Firebase Credentials
```bash
# Download service account key
# Go to Firebase Console > Project Settings > Service Accounts
# Click "Generate new private key"
# Save the JSON file securely
```

#### Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Questions collection
    match /questions/{questionId} {
      allow read, write: if request.auth != null;
    }
    
    // Media analyses collection
    match /media_analyses/{analysisId} {
      allow read, write: if request.auth != null;
    }
    
    // Candidate scores collection
    match /candidate_scores/{scoreId} {
      allow read, write: if request.auth != null;
    }
    
    // Interview sessions collection
    match /interview_sessions/{sessionId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### 5. Pinecone Setup

#### Create Pinecone Account
1. Sign up at [pinecone.io](https://pinecone.io)
2. Get API key and environment details
3. Create index:
```python
import pinecone
pinecone.init(api_key="your-api-key", environment="your-environment")
pinecone.create_index("recruitedge-questions", dimension=1536, metric="cosine")
```

### 6. Environment Configuration

#### Create .env File
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# S3 Configuration
S3_BUCKET_NAME=ai-recruitedge-media

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=recruitedge-questions

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/serviceAccountKey.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
LOG_LEVEL=INFO

# Security Configuration
CORS_ORIGINS=*
API_KEY_HEADER=X-API-Key
API_KEY=your_api_key_here

# Feature Flags
ENABLE_EMBEDDINGS=true
ENABLE_VECTOR_STORE=true
ENABLE_DATABASE=true

# Media Processing Configuration
MAX_FILE_SIZE=100
ALLOWED_MEDIA_TYPES=mp4,avi,mov,wav,mp3
TRANSCRIPTION_LANGUAGE=en-US
ANALYSIS_TIMEOUT=300

# Cleanup Configuration
CLEANUP_DAYS_OLD=30

# File Storage Configuration
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
```

### 7. Application Startup

#### Development Mode
```bash
python main.py
```

#### Production Mode
```bash
# Using Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using systemd service (Linux)
sudo nano /etc/systemd/system/recruitedge.service
```

#### Systemd Service File
```ini
[Unit]
Description=AI RecruitEdge MCP Server
After=network.target

[Service]
Type=simple
User=recruitedge
WorkingDirectory=/opt/recruitedge
Environment=PATH=/opt/recruitedge/venv/bin
ExecStart=/opt/recruitedge/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Production Deployment

### 1. Direct Server Deployment

#### Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.9 python3.9-venv python3.9-dev build-essential

# Create application user
sudo useradd -m -s /bin/bash recruitedge
sudo usermod -aG sudo recruitedge

# Switch to application user
sudo su - recruitedge

# Clone application
git clone https://github.com/your-repo/ai-recruitedge.git
cd ai-recruitedge

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads temp

# Set permissions
chmod 755 uploads temp
```

#### Environment Configuration
```bash
# Create environment file
nano .env
# Add all environment variables as shown above

# Set proper permissions
chmod 600 .env

# Create Firebase service account key
nano firebase-key.json
# Paste your Firebase service account key
chmod 600 firebase-key.json
```

#### Process Management
```bash
# Install PM2 for process management
npm install -g pm2

# Create PM2 ecosystem file
nano ecosystem.config.js
```

#### PM2 Configuration
```javascript
module.exports = {
  apps: [{
    name: 'recruitedge',
    script: 'main.py',
    interpreter: './venv/bin/python',
    cwd: '/opt/recruitedge',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

#### Start Application
```bash
# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

### 2. Nginx Configuration

#### Install Nginx
```bash
sudo apt install nginx
```

#### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/recruitedge
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /uploads {
        alias /opt/recruitedge/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/recruitedge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL Configuration

#### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

#### Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 4. Monitoring & Observability

#### CloudWatch Configuration
```yaml
# CloudWatch Logs
- logGroupName: /aws/recruitedge/application
  logStreamName: recruitedge-logs
  retentionInDays: 30

# CloudWatch Metrics
- metricName: RequestCount
  namespace: RecruitEdge
  dimensions:
    - Service: recruitedge
    - Environment: production

# CloudWatch Alarms
- alarmName: recruitedge-high-error-rate
  metricName: ErrorCount
  threshold: 10
  period: 300
  evaluationPeriods: 2
```

#### Prometheus Metrics
```python
# Add to main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 5. Security Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure Nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### API Key Authentication
```python
# Add to main.py
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_api_key(api_key: str = Security(security)):
    if api_key != config_service.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.post("/generate-questions")
async def generate_questions(
    request: QuestionGenerationRequest,
    api_key: str = Depends(verify_api_key)
):
    # Implementation
```

## Backup & Recovery

### 1. Firebase Backup
```bash
# Export Firestore data
gcloud firestore export gs://your-backup-bucket/recruitedge-backup/$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
BACKUP_BUCKET="your-backup-bucket"
DATE=$(date +%Y%m%d_%H%M%S)
gcloud firestore export gs://$BACKUP_BUCKET/recruitedge-backup/$DATE
```

### 2. File Backup
```bash
# S3 backup
aws s3 sync s3://ai-recruitedge-media s3://ai-recruitedge-backup/$(date +%Y%m%d)

# Local file backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### 3. Configuration Backup
```bash
# Backup environment files
cp .env .env.backup.$(date +%Y%m%d)
```

## Troubleshooting

### Common Issues

#### 1. AWS Credentials
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Bedrock access
aws bedrock list-foundation-models
```

#### 2. Firebase Connection
```python
# Test Firebase connection
import firebase_admin
from firebase_admin import firestore

# Initialize Firebase
firebase_admin.initialize_app()
db = firestore.client()

# Test write operation
doc_ref = db.collection('test').document('test-doc')
doc_ref.set({'test': 'data'})
print("Firebase connection successful")
```

#### 3. Pinecone Connection
```python
# Test Pinecone connection
import pinecone
pinecone.init(api_key="your-key", environment="your-env")
print(pinecone.list_indexes())
```

#### 4. File Permissions
```bash
# Fix upload directory permissions
chmod 755 uploads/
chmod 755 temp/
```

#### 5. Memory Issues
```bash
# Monitor memory usage
htop
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Performance Optimization

#### 1. Firebase Optimization
```python
# Use batch operations for multiple writes
batch = db.batch()
for i in range(100):
    doc_ref = db.collection('questions').document()
    batch.set(doc_ref, {'data': f'item_{i}'})
batch.commit()

# Use indexes for complex queries
# Create composite indexes in Firebase Console
```

#### 2. Application Optimization
```python
# Connection pooling for Firebase
# Firebase handles this automatically

# Caching with Redis
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## License

This project is licensed under the MIT License. 