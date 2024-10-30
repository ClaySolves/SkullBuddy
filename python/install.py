import shutil
import subprocess
import sys
import os
import time

tessPaths = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\Program Files (x86)\Tesseract-OCR",
    r"C:\Tesseract-OCR",
]


# Function to find Tesseract installation
def findTesseractInstall():
    for path in tessPaths:
        tessExe = os.path.join(path, "tesseract.exe")
        if os.path.isfile(tessExe):
            return tessExe
    return None

def buildExec():
    try:
        print("Building Executable...")
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "main.spec"])
        print("Build Complete!")
    except subprocess.CalledProcessError:
        print("Failed to build executable")
        sys.exit(1)

def installRequirements():
    # install requirements.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Installing Libraries...")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies from requirements.txt.")
        sys.exit(1)

def writeConfig(var,newVal):
    with open("python/config.py","r") as file:
        lines = file.readlines()

    with open("python/config.py","w") as file:
        for line in lines:
            if line.startswith(var):
                file.write(f'{var} = {newVal}\n')
            else:
                file.write(line)

def findPytessPath():
    """Locate the Tesseract OCR executable path."""
    # find pytess path
    tessPath = 'r"' + shutil.which(findTesseractInstall()) + '"'
    
    # if can't find exit
    if not tessPath:
        print("NO TESSERACT?????????? Bro can you not follow simple instructions? what are you even doing...\n Go download tesseract installer from https://github.com/UB-Mannheim/tesseract/releases NOW!")
        sys.exit(1)
    
    return tessPath

def install():
    # Step 1: Install dependencies from requirements.txt
    time1 = time.time()
    print("Installing dependencies...")
    installRequirements()
    
    # Step 2: Find Tesseract path
    print("Locating Tesseract OCR...")
    tessPath = findPytessPath()
    if not tessPath:
        print("Tesseract OCR not found. Please install Tesseract and try again.")
        sys.exit(1)
    
    # Step 3: Write the path to the config file
    writeConfig("pytessPath",tessPath)

    buildExec()
    time2 = time.time()
    print(f"Installation complete in {time2-time1:.1f} seconds. Check dist for SquireBot.exe")

if __name__ == "__main__":
    install()