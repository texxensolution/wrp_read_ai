#!/usr/bin/env bash
current_dir=$(pwd)
project_dir="$HOME/github/wrp_read_ai"
script_reading_dir="$project_dir/storage/script_reading"
quote_translation_dir="$project_dir/storage/quote_translation"
photo_interpretation_dir="$project_dir/storage/photo_interpretation"
myenv_dir="$project_dir/myenv"
$service_name="readai_worker.service"

cd "$project_dir"

echo "running git pull..."

git pull

echo "creating virtual environment..."
if [ -d "$project_dir"]; then
    echo "activating existing virtual environment..."
    source myenv/bin/activate
else
    echo "creating virtual environment..."
    python -m venv myvenv
    echo "activating virtual environment..."
    source myenv/bin/activate
fi

echo "install python dependencies..."
pip install -r requirements.txt

# create a necessary folders for audio storage
if [-d "$script_reading_dir"]; then
    echo "storage/script_reading folder created..."
    mkdir  storage/script_reading
else
    rm -rf storage/script_reading/*
fi

if [-d "$quote_translation_dir"]; then
    echo "storage/quote_translation folder created..."
    mkdir storage/quote_translation
else
    rm -rf storage/quote_translation/*
fi

if [-d "$photo_interpretation"]; then
    echo "storage/photo_interpretation folder created..."
    mkdir storage/photo_interpretation
else
    rm -rf storage/photo_interpretation/*
fi

if systemctl list-units --type=service --all | grep -q "$service_name"; then
    if systemctl is-active --quiet "$service_name"; then
        echo "stopping existing readai_worker service unit..."
        sudo systemctl stop readai_worker.service
    fi

    echo "overwriting readai_worker.service..."
    sudo cp $project_dir/scripts/readai_worker.service /etc/systemd/system
fi

sudo systemctl restart readai_worker.service
