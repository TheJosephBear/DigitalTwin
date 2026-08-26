#!/bin/bash

cd DigitalTwinWebsite

# Activate virtual environment and run fill_mongo_projects.py
echo "Preparing environment for fill_mongo_projects.py..."

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

# Run fill_mongo_projects.py
echo "Running fill_mongo_projects.py..."
cd DigitalTwinWebsite/code
python fill_mongo_projects.py --owner x "$@"
read -p "Press Enter to continue..."
