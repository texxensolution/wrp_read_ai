# ReadAI - Custom Background Worker that can be run as a systemd service unit.

The main purpose of this background worker is to assess and evaluate three types of assessment (script reading, quote translation, photo interpretation).
To run this program you can create a systemd.service script to run it as a background process in any Linux Machine that can run Python Interpreter.

Before deploying running it as a background process, make sure to install necessary dependencies specified in requirements.txt below you can find detail instruction to run this system as a background process.

## Steps to run the code

1. First make sure to have python installed in your local machine. \
   ```python -v```
2. Clone the repository \
   ```git clone https://github.com/texxensolution/wrp_read_ai.git```
3. cd into the cloned repository \
   ```cd wrp_read_ai```
4. Install necessary dependencies listed in requirements.txt \
   ```pip install -r requirements.txt```
5. To run it as a script you can just the main.py \
   ```python main.py```
