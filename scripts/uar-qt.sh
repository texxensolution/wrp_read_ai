current_dir=$(pwd)

echo "Stopping quote interpretation service..."
sudo systemctl stop quote_worker.service

cd "$HOME/github/wrp_read_ai"
echo "stashing the current state"
git stash

echo "pulling the updated project from github..."
git pull

sudo systemctl restart quote_worker.service