# PrepGenie Deployment Setup Script for Windows PowerShell
# Run: powershell -ExecutionPolicy Bypass -File deploy.ps1

param(
    [switch]$Build,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Clean
)

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Docker {
    try {
        $null = docker --version
        Write-Host "✅ Docker is installed" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker is not installed" -ForegroundColor Red
        Write-Host "Visit: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
}

function Test-DockerCompose {
    try {
        $null = docker-compose --version
        Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
        return $false
    }
}

function Setup-Environment {
    if (-not (Test-Path ".env")) {
        Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "📝 Edit .env with your credentials:" -ForegroundColor Yellow
        Write-Host "   - SUPABASE_URL"
        Write-Host "   - SUPABASE_SERVICE_ROLE_KEY"
        Write-Host "   - GEMINI_API_KEY"
        Write-Host "   - REACT_APP_SUPABASE_URL"
        Write-Host "   - REACT_APP_SUPABASE_ANON_KEY"
        Write-Host ""
        notepad .env
    }
}

function Build-Images {
    Write-Header "🔧 Building Docker Images"
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit 1
    }
}

function Start-Services {
    Write-Header "📦 Starting Services"
    docker-compose up -d
    
    Write-Host "⏳ Waiting for services to start..."
    Start-Sleep -Seconds 5
    
    $status = docker-compose ps
    Write-Host $status
    
    if ($status -match "Up") {
        Write-Host "✅ Services are running!" -ForegroundColor Green
        Show-URLs
    }
    else {
        Write-Host "❌ Services failed to start" -ForegroundColor Red
        Show-Logs
    }
}

function Stop-Services {
    Write-Header "🛑 Stopping Services"
    docker-compose down
    Write-Host "✅ Services stopped" -ForegroundColor Green
}

function Show-Logs {
    Write-Header "📋 Service Logs"
    docker-compose logs -f
}

function Show-URLs {
    Write-Host ""
    Write-Host "🌐 Access URLs:" -ForegroundColor Green
    Write-Host "   Frontend:  http://localhost"
    Write-Host "   Backend:   http://localhost:8000"
    Write-Host "   Health:    http://localhost:8000/health"
    Write-Host ""
    Write-Host "📚 Useful Commands:" -ForegroundColor Green
    Write-Host "   View logs:     docker-compose logs -f"
    Write-Host "   Stop services: docker-compose down"
    Write-Host "   Bash backend:  docker-compose exec backend bash"
    Write-Host ""
}

function Clean-Deployment {
    Write-Header "🧹 Cleaning Deployment"
    Write-Host "⚠️  This will remove all containers, networks, and volumes." -ForegroundColor Yellow
    $confirm = Read-Host "Continue? (yes/no)"
    
    if ($confirm -eq "yes") {
        docker-compose down -v
        Write-Host "✅ Cleanup completed" -ForegroundColor Green
    }
    else {
        Write-Host "Cancelled" -ForegroundColor Yellow
    }
}

# Main Script
Write-Host ""
Write-Host "🚀 PrepGenie Deployment Setup" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta

# Check Docker
if (-not (Test-Docker)) {
    exit 1
}

if (-not (Test-DockerCompose)) {
    exit 1
}

Write-Host ""

# Setup
Setup-Environment

# Process parameters or show menu
if ($Build) {
    Build-Images
    Start-Services
}
elseif ($Start) {
    docker-compose up -d
    Start-Sleep -Seconds 3
    Show-URLs
}
elseif ($Stop) {
    Stop-Services
}
elseif ($Logs) {
    Show-Logs
}
elseif ($Clean) {
    Clean-Deployment
}
else {
    # Show menu
    Write-Host "What would you like to do?" -ForegroundColor Cyan
    Write-Host "1. Build and Start" -ForegroundColor Yellow
    Write-Host "2. Start" -ForegroundColor Yellow
    Write-Host "3. Stop" -ForegroundColor Yellow
    Write-Host "4. View Logs" -ForegroundColor Yellow
    Write-Host "5. Clean" -ForegroundColor Yellow
    Write-Host "6. Exit" -ForegroundColor Yellow
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        "1" { Build-Images; Start-Services }
        "2" { 
            $null = docker-compose up -d
            Start-Sleep -Seconds 3
            Show-URLs 
        }
        "3" { Stop-Services }
        "4" { Show-Logs }
        "5" { Clean-Deployment }
        "6" { exit }
        default { Write-Host "Invalid choice" -ForegroundColor Red }
    }
}

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
