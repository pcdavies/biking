## Python Environment Setup with pyenv

## Notes:
- only the buildSummaryFile.py is working
- Put fit files from strava into the fitData directory - NOTE: Stored in my Dropbox

1. **Set the local Python version for this project:**
   ```sh
   pyenv install 3.11

   pyenv local 3.11
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Upgrade pip and install dependencies:**
   ```sh
   pip install --upgrade pip
   
   
