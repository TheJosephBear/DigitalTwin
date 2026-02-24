# Navigate to DigitalTwinWebsite
Set-Location DigitalTwinWebsite

# Activate virtual environment and run Flask app locally
Write-Host "Starting Flask app locally..."

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

# Run the Flask app
Write-Host "Running Flask app on http://localhost:5000"
Set-Location DigitalTwinWebsite\code
$env:FLASK_ENV = "local"
python App.py --local
Read-Host "Press Enter to continue..."
