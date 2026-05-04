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
    
    for page_num in range(1, 25):
        url = f"{BASE_URL}statewiseS22{page_num}.htm"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 404:
                break
                
            tables = pd.read_html(io.StringIO(response.text))
            df = tables[0] 
            
            for index, row in df.iterrows():
                # Skip header rows
                if pd.isna(row[0]) or "Constituency" in str(row[0]): 
                    continue
                
                # 1. Clean the Constituency Name (Removes (SC)/(ST) tags which break matching)
                raw_ac = str(row[0]).replace("(SC)", "").replace("(ST)", "").strip().title()
                ac_name = NAME_MAPPING.get(raw_ac, raw_ac)
                
                try:
                    # 2. Extract the correct shifted columns
                    raw_candidate = str(row[2]).strip()   
                    raw_party = str(row[3]).strip() 
                    raw_margin = str(row[6]).strip()      
                    raw_status = str(row[7]).strip()      
                    
                    # 3. Group Alliances so the Map Colors Work (DMK+, AIADMK+, etc.)
                    party_check = raw_party.upper()
                    
                    if "VETTRI" in party_check or "TVK" in party_check:
                        clean_party = "TVK"
                    elif "ANNA" in party_check or "AIADMK" in party_check or "DMDK" in party_check or "SDPI" in party_check or "PUTHIYA" in party_check:
                        clean_party = "AIADMK" # Colors map Green
                    elif "DRAVIDA" in party_check or "DMK" in party_check or "CONGRESS" in party_check or "INC" in party_check or "VCK" in party_check or "CPI" in party_check or "COMMUNIST" in party_check or "MDMK" in party_check:
                        clean_party = "DMK" # Colors map Red
                    elif "NAAM" in party_check or "NTK" in party_check:
                        clean_party = "NTK" # Colors map Dark Red
                    elif "JANATA" in party_check or "BJP" in party_check or "PMK" in party_check or "PATTALI" in party_check or "AMMK" in party_check:
                        clean_party = "BJP" # Colors map Orange
                    else:
                        clean_party = "OTH" # Defaults to Gray
                        
                    all_results[ac_name] = {
                        "candidate": raw_candidate.title(), 
                        "party": clean_party,
                        "margin": f"+{raw_margin}", 
                        "status": raw_status
                    }
                except IndexError:
                    # Safely skip if a row is malformed
                    continue
                    
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
