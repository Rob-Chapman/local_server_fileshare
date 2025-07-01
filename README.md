A tiny python script that lets the user choose a file or folder, then automatically sets up a local server and copies the URL into the user's clipboard. Vibe-coded after Windows' 'Nearby Share' feature failed to nearby share. 

INSTRUCTIONS:
Run the .exe file, select the file or folder to share, and send the URL to your intended recipient. When you're done sharing, just close the window.

BUILD INSTRUCTIONS:
python -m pip install --user pyinstaller
python -m PyInstaller --onefile --windowed share.py
