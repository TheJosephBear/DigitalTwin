#!/bin/bash

cd DigitalTwinWebsite

# Activate virtual environment and run Flask app locally
echo "Starting Flask app locally..."

# Check if venv exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    echo "Installing requirements..."
    venv/bin/pip install -r requirements.txt
fi

# Activate virtual environment
source venv/bin/activate

cd ..

# Load environment variables from .env.local file
if [ -f ".env.local" ]; then
    echo "Loading environment variables from .env.local file..."
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remove leading/trailing whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            export "$key=$value"
        fi
    done < ".env.local"
else
    echo "Warning: .env.local file not found. Using default values."
    export MONGO_URI=mongodb://localhost:27017
    export MONGO_DBNAME=digitalTwin
    export SECRET_KEY="'secret'"
fi

# Run the Flask app
echo "Running Flask app on http://localhost:5000"
cd DigitalTwinWebsite/code
export FLASK_ENV=local
python App.py --local
read -p "Press Enter to continue..."
