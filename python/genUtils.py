

#update config.py
def updateConfig(var,newVal) -> bool: # ret True/False updated
    logger.debug(f"Updating config {var} -> {newVal}")
    with open("python/config.py","r") as file:
        lines = file.readlines()

    with open("python/config.py","w") as file:
        for line in lines:
            if line.startswith(var):
                if isinstance(newVal,str):
                    file.write(f'{var} = "{newVal}"\n')
                else:
                    file.write(f'{var} = {newVal}\n')
            else:
                file.write(line)