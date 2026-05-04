import pandas as pd
import requests
import json
import os
import io

# The exact website URL you provided
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/"

# Dictionary to map ECI's exact spellings to your GeoJSON boundaries
NAME_MAPPING = {
    "Tiruchirappalli West": "Trichy West",
    "Chepauk-Thiruvallikeni": "Chepauk",
    "Thiyagarayanagar": "T. Nagar",
    "Dr. Radhakrishnan Nagar": "RK Nagar",
    "Coimbatore (South)": "Coimbatore South",
    "Coimbatore (North)": "Coimbatore North",
    "Erode (East)": "Erode East",
    "Erode (West)": "Erode West",
    "Salem (South)": "Salem South",
    "Salem (North)": "Salem North",
    "Salem (West)": "Salem West",
    "Madurai (East)": "Madurai East",
    "Madurai (West)": "Madurai West",
    "Madurai (Central)": "Madurai Central",
    "Madurai (South)": "Madurai South",
    "Madurai (North)": "Madurai North"
}

def get_eci_data():
    all_results = {}
    
    # Loop through all potential pages (Tamil Nadu usually spans across 20+ pages)
    for page_num in range(1, 25):
        # We append the State Code (S22) and the page number to your Base URL
        url = f"{BASE_URL}statewiseS22{page_num}.htm"
        
        try:
            # Standard browser User-Agent prevents the ECI from blocking the GitHub server
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=15)
            
            # If we hit a 404 error, we've reached the end of the data pages
            if response.status_code == 404:
                break
                
            # Parse the HTML tables using Pandas & StringIO
            tables = pd.read_html(io.StringIO(response.text))
            df = tables[0] 
            
            for index, row in df.iterrows():
                # Skip header rows or completely empty rows
                if pd.isna(row[0]) or "Constituency" in str(row[0]): 
                    continue
                
                # Clean up the raw name from the ECI table
                raw_ac = str(row[0]).strip().title()
                
                # Check if it needs to be mapped to match your GeoJSON
                ac_name = NAME_MAPPING.get(raw_ac, raw_ac)
                
                all_results[ac_name] = {
                    "candidate": str(row[1]).strip(),
                    "party": str(row[2]).strip(),
                    "margin": str(row[4]).strip(), 
                    "status": str(row[3]).strip()  
                }
            print(f"Successfully scraped page {page_num}")
            
        except ValueError:
            print(f"No tables found on page {page_num}. Ending scrape.")
            break
        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            break
            
    return all_results

def main():
    print(f"Fetching LIVE 2026 Counting Data from {BASE_URL}...")
    results = get_eci_data()
    
    if results:
        os.makedirs('data', exist_ok=True)
        with open('data/map_data.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Success! Updated map_data.json with {len(results)} live constituencies.")
    else:
        print("Failed to fetch live data. The ECI server may be experiencing high load.")

if __name__ == "__main__":
    main()
