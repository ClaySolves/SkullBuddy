import difflib
import DAD_Utils

def findItem(input_string, phrase_list):
    closest_match = difflib.get_close_matches(input_string, phrase_list, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None

# str = '+ - +18 Luck -'
# str = ''.join([char for char in str if char.isalpha()])
# print(str)

# with open("rolls.txt", 'r') as file:
#         lines = file.readlines()
# allItems = [line.strip() for line in lines]

# res = findItem(str,allItems)

# print(res)

print(DAD_Utils.getCurrentScreen('showListingComplete'))