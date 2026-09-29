# DevTrack AI - Local PowerShell Helper Script

param (
    [string]$action = "help"
)

switch ($action) {
    "test" {
        Write-Host "Running pytest test suite..." -ForegroundColor Cyan
        & "app/backend/.venv/Scripts/python.exe" -m pytest tests/ -v
    }
    "compose-up" {
        Write-Host "Starting Docker Compose stack..." -ForegroundColor Cyan
        docker compose -f docker/docker-compose.yml up --build -d
    }
    "compose-down" {
        Write-Host "Stopping Docker Compose stack..." -ForegroundColor Cyan
        docker compose -f docker/docker-compose.yml down
    }
    "status" {
        Write-Host "Git Status:" -ForegroundColor Yellow
        git status
        Write-Host "`nDocker Containers:" -ForegroundColor Yellow
        docker ps
    }
    default {
        Write-Host "DevTrack AI PowerShell Commands:" -ForegroundColor Green
        Write-Host "  .\scripts\dev.ps1 test          - Run all unit and integration tests"
        Write-Host "  .\scripts\dev.ps1 compose-up     - Start Postgres, Backend, and Frontend containers"
        Write-Host "  .\scripts\dev.ps1 compose-down   - Stop Docker containers"
        Write-Host "  .\scripts\dev.ps1 status         - Show git & docker container status"
    }
}
