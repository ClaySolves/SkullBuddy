import difflib

def findItem(input_string, phrase_list):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None

str = '4 Troll�s Bane'

with open("items.txt", 'r') as file:
        lines = file.readlines()
allItems = [line.strip() for line in lines]

res = findItem(str,allItems)

print(res)