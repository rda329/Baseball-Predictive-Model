#MLB Team Salary data 1985-2010 
#Source: https://www.kaggle.com/datasets/open-source-sports/baseball-databank?resource=download

#This script will scrape MLB team salary data for years 2011-2024
#Source: https://www.spotrac.com/mlb/payroll/_/year/2024

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def scrape_salary(year):
    url = f"https://www.spotrac.com/mlb/payroll/year/{year}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for year {year}: {str(e)}")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    team_salaries = {}
    
    # Find the main payroll table
    table = soup.find('table', {'class': 'datatable'})
    if not table:
        print(f"Could not find payroll table for year {year}")
        return None
    
    # Get all rows in the table body
    rows = table.find('tbody').find_all('tr')
    
    for row in rows:
        try:
            # Get team initials from the span with class "d-none"
            initials_element = row.find('span', {'class': 'd-none'})
            if not initials_element:
                continue
                
            initials = initials_element.text.strip()
            
            # Finding the active salary cell (usually the 5th numeric column)
            salary_cells = row.find_all('td', {'class': lambda x: x and 'sorting_1' in x and 'dt-type-numeric' in x})
            if salary_cells:
                salary_text = salary_cells[0].text.strip()
                # Clean up the salary text (remove $ and commas)
                salary = int(salary_text.replace('$', '').replace(',', ''))
                
                team_salaries[initials] = salary
                
        except Exception as e:
            print(f"Error processing row: {str(e)}")
            continue
    
    return team_salaries

def main():
    salaries = {}
    
    # Example: Scrape data for 2025
    year = 2025
    print(f"Scraping data for year {year}...")
    year_data = scrape_salary(year)
    
    if year_data:
        salaries[year] = year_data
    
    # Save to JSON file
    with open('mlb_salaries.json', 'w') as f:
        json.dump(salaries, f, indent=2)
    
    print("Scraping complete. Data saved to mlb_salaries.json")
    print(json.dumps(salaries, indent=2))  # Print the collected data

if __name__ == "__main__":
    main()

# Data Struct
#   {
#     year: {
#         team_initials: active_26_man_salary
#     }
# }