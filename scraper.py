import pandas as pd
import requests
import json
import os

# Official ECI 2026 Tamil Nadu State Code is S22
BASE_URL = "https://results.eci.gov.in/ResultAcGenMay2026/statewiseS22"

# Mapping ECI names to your Dashboard names (Add more as needed)
NAME_MAPPING = {
    "Tiruchirappalli West": "Trichy West",
    "Chepauk-Thiruvallikeni": "Chepauk",
    "Thiyagarayanagar": "T. Nagar",
    "Dr. Radhakrishnan Nagar": "RK Nagar"
}

def get_eci_data():
    all_results = {}
    
    # ECI results are often spread across multiple sub-pages (1 to 9)
    for page_num in range(1, 10):
        url = f"{BASE_URL}{page_num}.htm"
        try:
            # We use headers to mimic a browser to avoid getting blocked
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            tables = pd.read_html(response.text)
            
            # The result table is usually the first or second table on the page
            df = tables[0] 
            
            # Identify columns based on ECI's 2026 layout
            # Expected columns: [Constituency, Leading Candidate, Party, Status, Margin]
            for index, row in df.iterrows():
                # Skip header rows
                if "Constituency" in str(row[0]): continue
                
                raw_ac = str(row[0]).strip()
                ac_name = NAME_MAPPING.get(raw_ac, raw_ac)
                
                all_results[ac_name] = {
                    "candidate": str(row[1]).strip(),
                    "party": str(row[2]).strip(),
                    "margin": str(row[4]).strip(), # Usually the 5th column
                    "status": str(row[3]).strip()  # 'Leading' or 'Won'
                }
        except Exception as e:
            print(f"Finished or Error on page {page_num}: {e}")
            break
            
    return all_results

def main():
    print("Fetching live trends from ECI...")
    results = get_eci_data()
    
    if results:
        os.makedirs('data', exist_ok=True)
        with open('data/map_data.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Successfully synced {len(results)} constituencies.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()