"""Fetch official Google Street View panorama IDs for Pittsburgh locations."""
import json
import requests
import time
import random

# Locations placed directly on roads/sidewalks for better official street view coverage
LOCATIONS = [
    # Downtown
    {"lat": 40.44079, "lng": -79.99565, "name": "Market Square"},
    {"lat": 40.43815, "lng": -79.98482, "name": "PPG Place"},
    {"lat": 40.43750, "lng": -79.97770, "name": "Smithfield St Bridge"},
    {"lat": 40.44250, "lng": -80.00330, "name": "Fort Duquesne Blvd"},
    {"lat": 40.44110, "lng": -79.99200, "name": "Liberty Ave Downtown"},
    {"lat": 40.43950, "lng": -79.99000, "name": "Grant St"},
    {"lat": 40.43700, "lng": -79.98800, "name": "Boulevard of the Allies"},
    # North Side
    {"lat": 40.44675, "lng": -80.00568, "name": "PNC Park"},
    {"lat": 40.45380, "lng": -80.00240, "name": "North Shore - Federal St"},
    {"lat": 40.46985, "lng": -80.01190, "name": "Deutschtown - E Ohio St"},
    {"lat": 40.46765, "lng": -80.02158, "name": "Troy Hill"},
    {"lat": 40.46020, "lng": -79.95450, "name": "Spring Garden"},
    # South Side
    {"lat": 40.42927, "lng": -79.97941, "name": "South Side - E Carson St"},
    {"lat": 40.43370, "lng": -79.97230, "name": "South Side Slopes"},
    {"lat": 40.43487, "lng": -80.01027, "name": "Grandview Ave"},
    {"lat": 40.43270, "lng": -80.01895, "name": "Duquesne Incline"},
    # Oakland / University
    {"lat": 40.44424, "lng": -79.95317, "name": "Oakland - Forbes Ave"},
    {"lat": 40.44439, "lng": -79.94833, "name": "Cathedral of Learning"},
    {"lat": 40.43930, "lng": -79.93470, "name": "CMU Campus"},
    {"lat": 40.43295, "lng": -79.96270, "name": "Oakland - Semple St"},
    {"lat": 40.44850, "lng": -79.96600, "name": "Herron Ave"},
    # East
    {"lat": 40.45315, "lng": -79.94880, "name": "Lawrenceville - Butler St"},
    {"lat": 40.45818, "lng": -79.93816, "name": "Bloomfield - Liberty Ave"},
    {"lat": 40.43539, "lng": -79.92303, "name": "Squirrel Hill - Murray Ave"},
    {"lat": 40.46165, "lng": -79.92526, "name": "East Liberty - Penn Ave"},
    {"lat": 40.44852, "lng": -79.93096, "name": "Shadyside - Walnut St"},
    {"lat": 40.45680, "lng": -79.91950, "name": "Garfield - Penn Ave"},
    {"lat": 40.46150, "lng": -79.90100, "name": "Highland Park - Bryant St"},
    {"lat": 40.43150, "lng": -79.91235, "name": "Frick Park - Reynolds St"},
    # Strip District
    {"lat": 40.45197, "lng": -79.97973, "name": "Strip District - Smallman St"},
    {"lat": 40.45456, "lng": -79.98012, "name": "Strip District - Penn Ave"},
    # West / South / Outer
    {"lat": 40.43526, "lng": -79.99736, "name": "Station Square"},
    {"lat": 40.41247, "lng": -79.93150, "name": "Greenfield - Greenfield Ave"},
    {"lat": 40.41950, "lng": -80.03839, "name": "Crafton - Noble Ave"},
    {"lat": 40.46580, "lng": -80.03850, "name": "Bellevue - Lincoln Ave"},
    {"lat": 40.39721, "lng": -79.91172, "name": "Homestead - E 8th Ave"},
    {"lat": 40.42035, "lng": -79.88210, "name": "Swissvale - Noble St"},
    {"lat": 40.44723, "lng": -79.87640, "name": "Wilkinsburg - Penn Ave"},
    {"lat": 40.41080, "lng": -79.94910, "name": "Hazelwood - 2nd Ave"},
    {"lat": 40.40810, "lng": -79.96680, "name": "Carrick - Brownsville Rd"},
    {"lat": 40.43570, "lng": -79.86700, "name": "Edgewood - Swissvale Ave"},
    {"lat": 40.47890, "lng": -79.90340, "name": "Aspinwall - Commercial Ave"},
    {"lat": 40.47105, "lng": -79.95917, "name": "Millvale - Grant Ave"},
    {"lat": 40.42230, "lng": -79.95250, "name": "Panther Hollow"},
    {"lat": 40.45010, "lng": -80.01720, "name": "West End Overlook"},
    {"lat": 40.44550, "lng": -79.99070, "name": "Andy Warhol Museum area"},
    # Additional road locations for better type-2 coverage
    {"lat": 40.44168, "lng": -79.99800, "name": "Point State Park area"},
    {"lat": 40.44090, "lng": -80.01225, "name": "West End Bridge"},
    {"lat": 40.43920, "lng": -79.95171, "name": "Schenley Drive"},
    {"lat": 40.44645, "lng": -79.95024, "name": "Polish Hill"},
    {"lat": 40.44400, "lng": -79.94300, "name": "Craig St"},
    {"lat": 40.45100, "lng": -79.93500, "name": "Penn Ave - Friendship"},
    {"lat": 40.43400, "lng": -79.95600, "name": "Bates St"},
    {"lat": 40.44700, "lng": -79.97400, "name": "Centre Ave - Hill District"},
    {"lat": 40.43600, "lng": -79.99100, "name": "First Ave"},
    {"lat": 40.44800, "lng": -80.00800, "name": "Allegheny Ave - North Side"},
    {"lat": 40.42500, "lng": -79.97300, "name": "Arlington Ave"},
    {"lat": 40.45500, "lng": -79.96300, "name": "Bigelow Blvd"},
    {"lat": 40.46300, "lng": -79.94500, "name": "Butler St - Upper Lawrenceville"},
    {"lat": 40.42800, "lng": -79.93800, "name": "Forward Ave"},
    {"lat": 40.43100, "lng": -79.89800, "name": "Beechwood Blvd"},
    {"lat": 40.45800, "lng": -79.97200, "name": "Penn Ave - Garfield"},
]

RPC_URL = "https://maps.googleapis.com/$rpc/google.internal.maps.mapsjs.v1.MapsJsInternalService/SingleImageSearch"
HEADERS = {
    "Content-Type": "application/json+protobuf",
    "Referer": "https://www.google.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

def get_pano_id(lat, lng, radius=50):
    """Fetch panorama ID from coordinates, preferring official Google Street View."""
    body = json.dumps([["apiv3"], [[None, None, lat, lng], radius], None, [[1, 2, 3, 4, 8, 6]]])
    try:
        resp = requests.post(RPC_URL, headers=HEADERS, data=body, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 1 and data[1]:
                pano_data = data[1]
                if len(pano_data) > 1 and pano_data[1] and len(pano_data[1]) > 1:
                    pano_id = pano_data[1][1]
                    img_type = pano_data[1][0] if pano_data[1] else None
                    actual_lat, actual_lng = lat, lng
                    try:
                        actual_lat = pano_data[5][0][1][0][2]
                        actual_lng = pano_data[5][0][1][0][3]
                    except (IndexError, TypeError):
                        pass
                    return {
                        "pano_id": pano_id,
                        "type": img_type,
                        "lat": actual_lat,
                        "lng": actual_lng,
                    }
    except Exception as e:
        print(f"  Error: {e}")
    return None

def main():
    type2_results = []
    type10_results = []

    for i, loc in enumerate(LOCATIONS):
        print(f"[{i+1}/{len(LOCATIONS)}] {loc['name']}...", end=" ", flush=True)

        # Try small radius first (prefer nearby official coverage)
        result = None
        for radius in [30, 80, 200, 500]:
            result = get_pano_id(loc["lat"], loc["lng"], radius=radius)
            if result and result["type"] == 2:
                break  # Found official pano, use it
            if result and result["type"] != 2 and radius < 500:
                continue  # Keep searching wider for official pano
            if result:
                break

        if result:
            bucket = "TYPE 2 (official)" if result["type"] == 2 else f"TYPE {result['type']} (photosphere)"
            print(f"{bucket} - {result['pano_id'][:25]}...")
            entry = {
                "name": loc["name"],
                "lat": round(result["lat"], 4),
                "lng": round(result["lng"], 4),
                "pano": result["pano_id"],
                "type": result["type"],
            }
            if result["type"] == 2:
                type2_results.append(entry)
            else:
                type10_results.append(entry)
        else:
            print("FAILED")

        time.sleep(0.25)

    print(f"\n\nType 2 (official): {len(type2_results)}")
    print(f"Type 10 (photosphere): {len(type10_results)}")

    # Use only type 2 for the game
    results = type2_results
    print(f"\nUsing {len(results)} official Google Street View locations.\n")

    print("const LOCATIONS = [")
    for r in results:
        print(f'  {{ lat: {r["lat"]}, lng: {r["lng"]}, name: "{r["name"]}", pano: "{r["pano"]}" }},')
    print("];")

    with open("locations_type2.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to locations_type2.json")

if __name__ == "__main__":
    main()
