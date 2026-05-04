import json
import random
import os

def generate_live_simulation():
    print("Initializing Simulation Mode...")
    
    try:
        # 1. Read your existing 234 seats from the districts file
        with open('data/tn_districts.json', 'r') as f:
            districts = json.load(f)
            
        parties = ['TVK', 'DMK', 'AIADMK']
        # Simulating the TVK wave: 55% chance of TVK, 30% DMK, 15% AIADMK
        weights = [0.55, 0.30, 0.15] 
        
        mock_results = {}
        
        # 2. Generate realistic data for every single seat
        for dist_name, seats in districts.items():
            for seat in seats:
                winning_party = random.choices(parties, weights=weights)[0]
                margin_num = random.randint(1500, 42000)
                
                mock_results[seat] = {
                    "candidate": f"Candidate ({winning_party})",
                    "party": winning_party,
                    "margin": f"+{margin_num:,}",
                    "status": random.choice(["Leading", "WON"])
                }
                
        # 3. Save it to map_data.json
        os.makedirs('data', exist_ok=True)
        with open('data/map_data.json', 'w') as f:
            json.dump(mock_results, f, indent=2)
            
        print(f"Success! Generated mock data for {len(mock_results)} constituencies.")
        
    except Exception as e:
        print(f"Error generating simulation: {e}")

if __name__ == "__main__":
    generate_live_simulation()
