# Navigate to DigitalTwinWebsite
Set-Location DigitalTwinWebsite

# Activate virtual environment and run fill_mongo_projects.py
Write-Host "Preparing environment for fill_mongo_projects.py..."

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating one..."
    python -m venv venv
    Write-Host "Installing requirements..."
    & venv\Scripts\pip install -r requirements.txt
}

# Activate virtual environment
& venv\Scripts\Activate.ps1

# Go back to parent directory
Set-Location ..

# Load environment variables from .env.local file
if (Test-Path ".env.local") {
    Write-Host "Loading environment variables from .env.local file..."
    Get-Content ".env.local" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*?)\s*=\s*(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Host "Warning: .env.local file not found. Using default values."
    $env:MONGO_URI = "mongodb://localhost:27017"
    $env:MONGO_DBNAME = "digitalTwin"
    $env:SECRET_KEY = "'secret'"
}

# Run fill_mongo_projects.py
Write-Host "Running fill_mongo_projects.py..."
Set-Location DigitalTwinWebsite\code
python fill_mongo_projects.py --owner x @args
Read-Host "Press Enter to continue..."
