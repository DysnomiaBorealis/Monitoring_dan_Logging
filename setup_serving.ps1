# Spam Detection Model Serving Setup Script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "SPAM DETECTION MODEL - DOCKER SERVING SETUP" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "      ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "      ✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Pull latest model image
Write-Host ""
Write-Host "[2/6] Pulling latest model from Docker Hub..." -ForegroundColor Yellow
docker pull dysnomiaborealis/workflow-ci-spam-detection:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ✗ Failed to pull Docker image" -ForegroundColor Red
    exit 1
}
Write-Host "      ✓ Image pulled successfully" -ForegroundColor Green

# Extract model from container
Write-Host ""
Write-Host "[3/6] Extracting trained model..." -ForegroundColor Yellow

# Create models directory if it doesn't exist
if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
}

# Create temporary container
docker create --name temp_spam_model dysnomiaborealis/workflow-ci-spam-detection:latest | Out-Null

# Copy model file
docker cp temp_spam_model:/app/models/spam_detection_model.joblib ./models/

if ($LASTEXITCODE -eq 0) {
    Write-Host "      ✓ Model extracted to ./models/" -ForegroundColor Green
} else {
    Write-Host "      ✗ Failed to extract model" -ForegroundColor Red
    docker rm temp_spam_model | Out-Null
    exit 1
}

# Remove temporary container
docker rm temp_spam_model | Out-Null

# Build serving image
Write-Host ""
Write-Host "[4/6] Building serving Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.serve -t spam-detection-serve:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ✗ Failed to build serving image" -ForegroundColor Red
    exit 1
}
Write-Host "      ✓ Serving image built successfully" -ForegroundColor Green

# Stop and remove existing container if running
Write-Host ""
Write-Host "[5/6] Cleaning up old containers..." -ForegroundColor Yellow
docker stop spam-serve 2>$null | Out-Null
docker rm spam-serve 2>$null | Out-Null
Write-Host "      ✓ Cleanup complete" -ForegroundColor Green

# Run serving container
Write-Host ""
Write-Host "[6/6] Starting serving container..." -ForegroundColor Yellow
docker run -d -p 5001:5001 --name spam-serve spam-detection-serve:latest | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ✗ Failed to start serving container" -ForegroundColor Red
    exit 1
}

# Wait for container to be healthy
Write-Host "      Waiting for service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test health endpoint
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get
    if ($response.status -eq "healthy") {
        Write-Host "      ✓ Serving container is running and healthy!" -ForegroundColor Green
    } else {
        Write-Host "      ⚠ Container started but model not loaded properly" -ForegroundColor Yellow
    }
} catch {
    Write-Host "      ⚠ Container started but health check failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host "Model serving is now running at: http://localhost:5001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test the endpoint:" -ForegroundColor Yellow
Write-Host '  Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get' -ForegroundColor White
Write-Host ""
Write-Host "Or run test suite:" -ForegroundColor Yellow
Write-Host "  python test_serving.py" -ForegroundColor White
Write-Host ""
