current_dir=$(pwd)

echo "Stopping script reading service..."
sudo systemctl stop sr_worker.service

cd "$HOME/github/wrp_read_ai"
echo "stashing the current state"
git stash

echo "pulling the updated project from github..."
git pull

sudo systemctl restart sr_worker.service