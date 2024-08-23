from bs4 import BeautifulSoup

# Load the saved HTML file
with open("dark_and_darker_weapons.html", "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML
soup = BeautifulSoup(content, 'html.parser')

# Find all tables
tables = soup.find_all('table')

# Iterate through each table and get the first column's data
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        # Get the first column of each row
        first_column = row.find_all('td')[0].text.strip()
        print(first_column)
