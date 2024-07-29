# ReadAI - Custom Background Worker that can be run as a systemd service unit.

The main purpose of this background worker is to assess and evaluate three types of assessment (script reading, quote translation, photo interpretation).
To run this program you can create a systemd.service script to run it as a background process in any Linux Machine that can run Python Interpreter.

Before deploying running it as a background process, make sure to install necessary dependencies specified in requirements.txt below you can find detail instruction to run this system as a background process.

# File Structure
data (compatibility with script reading) - this contains all references for script reading script
logs - this contains all logs emitted by the readai background processor
scripts - this contains all the automation and deployment scripts
storage - this holds the audio recordings temporarily before deletion after the assessment is processed
src - this contains the source code for the readai background processor
   • cli - contains cli interface to handle service redeployment, restart (not implemented yet)
   • common - this contains common code or general code that I cant properly place elsewhere :D
   • dtos - this contains all Data Transfer Objects its used to wrap data and provide better autocompletion
   • enums - this provide all enums that the project used
   • exception - this contains custom exceptions
   • interfaces - this contains all the contracts or interfaces
   • lark - this is a small library I wrote for interacting with Lark Base
   • prompts - this contains the llm prompts
   • services - this contains the service wrapper for different apis
   • stores - this handle data persistent

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
