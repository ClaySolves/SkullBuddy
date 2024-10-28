import shutil
import subprocess
import sys
import DAD_Utils

def installRequirements():
    # install requirements.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Installing Libraries...")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies from requirements.txt.")
        sys.exit(1)

def findPytessPath():
    """Locate the Tesseract OCR executable path."""
    # find pytess path
    tessPath = shutil.which("tesseract")
    
    # if can't find exit
    if not tessPath:
        print("NO PYTESS???? run 'pip install pytesseract' in your terminal right now and restart ")
        sys.exit(1)
    
    return tessPath

def install():
    # Step 1: Install dependencies from requirements.txt
    print("Installing dependencies...")
    installRequirements()
    
    # Step 2: Find Tesseract path
    print("Locating Tesseract OCR...")
    tessPath = findPytessPath()
    if not tessPath:
        print("Tesseract OCR not found. Please install Tesseract and try again.")
        sys.exit(1)
    
    # Step 3: Write the path to the config file
    DAD_Utils.updateConfig("pytessPath",tessPath)
    print("Installation complete.")