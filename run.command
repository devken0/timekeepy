#!/bin/sh

# $0 holds the path used to execute the script, needed for .command files to run properly
cd "$(dirname "$0")"

# Check if venv exists, if not, create it
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Check if the required packages are installed from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Checking for missing Python modules in requirements.txt..."

    # Install missing modules
    pip install --upgrade -r requirements.txt
else
    echo "requirements.txt not found. Skipping package installation."
fi

# Run the Python script
echo "Running main.py..."
python main.py