import shutil
import subprocess
import sys
import os
import time
import platform

tessPaths = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\Program Files (x86)\Tesseract-OCR",
    r"C:\Tesseract-OCR",
]


def handleMicrosoftBuild():
    ver = platform.version()
    verComp = int(ver.split('.')[2])
    rel = int(platform.release())
    buildInstallCommand = None

    print(verComp, rel)

    if rel == 10 and verComp < 22000:
        print("Getting Microsoft Visual C++ build Tools for Windows 10")
        buildInstallCommand = [
        "winget", "install", "Microsoft.VisualStudio.2022.BuildTools",
        "--force", "--override",
        '"--wait --passive --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK"'
        ]
    elif rel == 11 and verComp >=22000:
        print("Getting Microsoft Visual C++ build Tools for Windows 11")
        buildInstallCommand = [
        "winget", "install", "Microsoft.VisualStudio.2022.BuildTools",
        "--force", "--override",
        '"--wait --passive --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22621"'
        ]
    else:
        print("Download Getting Microsoft Visual C++ build Tools for Windows 11 @")
        print("https://aka.ms/vs/17/release/vs_BuildTools.exe")

    if buildInstallCommand:
        subprocess.run(" ".join(buildInstallCommand), shell=True, check=True)

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
        time.sleep(1)
    except subprocess.CalledProcessError:
        print("Failed to build executable")
        sys.exit(1)


def installRequirements():
    # install requirements.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "python/requirements.txt"])
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

    # find pytess path
    foundPath = findTesseractInstall()

    if not foundPath:
        print("NO TESSERACT?????????? Bro can you not follow simple instructions? what are you even doing...\n Go download tesseract installer from https://github.com/UB-Mannheim/tesseract/releases NOW!")
        sys.exit(1)

    tessPath = 'r"' + shutil.which(findTesseractInstall()) + '"'
    
    return tessPath


def install():
    # Step 1: Install dependencies from requirements.txt
    time1 = time.time()
    print("Fetching Visual C++ Build Tools...")
    handleMicrosoftBuild()
    
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
    print(f"Installation complete in {time2-time1:.1f} seconds. Check dist for SkullBuddy.exe")


if __name__ == "__main__":
    install()