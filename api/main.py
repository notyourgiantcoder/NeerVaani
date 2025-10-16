#!/usr/bin/env python3
"""
Standalone FloatChat API Server - No External Dependencies
"""

from flask import Flask, request, jsonify
import random
import json
import re
from datetime import datetime

app = Flask(__name__)

# Manual CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def _build_rng(lat: float, lon: float, query_lower: str) -> random.Random:
    """Create a deterministic RNG so similar queries vary but are stable per query/location."""
    seed = hash((round(lat, 2), round(lon, 2), query_lower)) & 0xFFFFFFFF
    return random.Random(seed)

def _parse_location_from_query(query_lower: str):
    """Try to extract latitude/longitude from the query text.
    Supports patterns like 'lat 12.9 lon 77.6', 'latitude: 12.9, longitude: 77.6',
    or compact '12.9N 77.6E'. Returns (lat, lon) or None.
    """
    # Pattern 1: lat ... lon ...
    m1 = re.search(r"lat(?:itude)?\s*[:=]?\s*(-?\d{1,2}(?:\.\d+)?)", query_lower)
    m2 = re.search(r"lon(?:gitude)?\s*[:=]?\s*(-?\d{1,3}(?:\.\d+)?)", query_lower)
    if m1 and m2:
        try:
            lat = float(m1.group(1))
            lon = float(m2.group(1))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except ValueError:
            pass

    # Pattern 2: 12.9N 77.6E (or S/W)
    m3 = re.search(r"(-?\d{1,2}(?:\.\d+)?)([ns])\s+(-?\d{1,3}(?:\.\d+)?)([ew])", query_lower)
    if m3:
        lat = float(m3.group(1)) * (1 if m3.group(2) == 'n' else -1)
        lon = float(m3.group(3)) * (1 if m3.group(4) == 'e' else -1)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon

    return None

def _infer_intent(query_lower: str):
    """Infer user's focus parameter and mode to diversify responses."""
    temp_kw = ["temp", "temperature", "thermocline", "warm", "cold"]
    sal_kw = ["salinity", "salt", "halocline"]
    oxy_kw = ["oxygen", "o2", "dissolved oxygen"]
    trend_kw = ["trend", "increase", "decrease", "change", "over time", "season", "monthly", "yearly"]
    extreme_kw = ["max", "min", "peak", "highest", "lowest", "anomaly", "anomalies"]

    primary = "profile"
    if any(k in query_lower for k in temp_kw):
        primary = "temperature"
    elif any(k in query_lower for k in sal_kw):
        primary = "salinity"
    elif any(k in query_lower for k in oxy_kw):
        primary = "oxygen"

    if any(k in query_lower for k in trend_kw):
        mode = "trend"
    elif any(k in query_lower for k in extreme_kw):
        mode = "extremes"
    else:
        mode = "structure"

    detail = "standard"
    if "detailed" in query_lower or "high-resolution" in query_lower:
        detail = "detailed"

    return {"primary": primary, "mode": mode, "detail": detail}

def generate_realistic_profile(lat, lon, query_lower, rng: random.Random = None):
    """Generate scientifically plausible oceanographic profiles based on location and intent."""
    if rng is None:
        rng = _build_rng(lat, lon, query_lower)
    
    # Determine regional oceanographic characteristics
    if abs(lat) <= 10:  # Tropical
        surface_temp = rng.uniform(26, 29)
        surface_salinity = rng.uniform(34.5, 35.5)
        thermocline_strength = 0.18  # Strong thermocline
    elif 10 < abs(lat) <= 30:  # Subtropical
        surface_temp = rng.uniform(22, 27)
        surface_salinity = rng.uniform(35.0, 36.5)
        thermocline_strength = 0.14
    elif 30 < abs(lat) <= 50:  # Temperate
        surface_temp = rng.uniform(15, 22)
        surface_salinity = rng.uniform(34.0, 35.5)
        thermocline_strength = 0.10
    else:  # Polar/Subpolar
        surface_temp = rng.uniform(2, 10)
        surface_salinity = rng.uniform(33.5, 34.5)
        thermocline_strength = 0.06
    
    # Regional modifications
    if "arabian" in query_lower or (50 < lon < 80 and 10 < lat < 25):
        surface_temp += rng.uniform(0.5, 2.0)  # Warmer Arabian Sea
        surface_salinity += rng.uniform(0.3, 0.8)  # Higher salinity due to evaporation
    elif "pacific" in query_lower and -180 < lon < -80:
        surface_temp += rng.uniform(-1.0, 1.0)  # Pacific variability
        if lat < 10:  # Equatorial Pacific
            surface_salinity -= rng.uniform(0.2, 0.5)  # Equatorial freshening
    
    # Generate depth levels with realistic oceanographic structure
    depths = []
    # Choose depth resolution based on query detail
    if any(k in query_lower for k in ["detailed", "high-res", "high resolution"]):
        pressures = [5, 10, 15, 25, 35, 50, 65, 80, 100, 125, 150]
    else:
        pressures = [5, 15, 30, 50, 75, 100, 125, 150]
    
    for i, pressure in enumerate(pressures):
        # Temperature: surface mixed layer + thermocline + deep water
        if pressure <= 20:  # Surface mixed layer
            temp = surface_temp + rng.uniform(-0.5, 0.5)
        elif pressure <= 100:  # Main thermocline
            depth_factor = (pressure - 20) / 80
            temp_drop = thermocline_strength * 80 * depth_factor
            temp = surface_temp - temp_drop + rng.uniform(-0.8, 0.8)
        else:  # Deep water
            temp = surface_temp - (thermocline_strength * 80) - (pressure - 100) * 0.02
            temp += rng.uniform(-0.5, 0.5)
        
        temp = max(temp, 1.5)  # Ocean minimum temperature
        
        # Salinity: surface layer + halocline + deep water
        if pressure <= 30:
            salinity = surface_salinity + rng.uniform(-0.1, 0.1)
        elif pressure <= 80:
            # Subsurface salinity maximum common in many regions
            salinity = surface_salinity + 0.1 + rng.uniform(-0.15, 0.15)
        else:
            # Deep water salinity
            salinity = surface_salinity - 0.05 + rng.uniform(-0.2, 0.2)
        
        salinity = max(min(salinity, 37.5), 32.0)  # Realistic ocean bounds
        
        depths.append({
            "pres": float(pressure),
            "temp": round(temp, 2),
            "salinity": round(salinity, 2)
        })
    
    return depths

def generate_detailed_analysis(depths, location_desc, lat, lon, query):
    """Generate sophisticated oceanographic insights"""
    
    surface = depths[0]
    deep = depths[-1]
    mid_depth = depths[len(depths)//2]
    
    # Calculate gradients and characteristics
    temp_gradient = (surface['temp'] - deep['temp']) / (deep['pres'] - surface['pres'])
    salinity_range = max([d['salinity'] for d in depths]) - min([d['salinity'] for d in depths])
    
    # Determine water mass characteristics
    if surface['temp'] > 24 and lat < 30 and lat > -30:
        water_mass = "tropical surface waters"
        climate_note = "This indicates warm tropical conditions typical of low latitudes."
    elif surface['temp'] < 15 and abs(lat) > 40:
        water_mass = "temperate/subpolar waters" 
        climate_note = "These cooler temperatures suggest mid to high latitude conditions."
    elif surface['temp'] > 20 and 50 < lon < 80 and 10 < lat < 25:
        water_mass = "Arabian Sea surface waters"
        climate_note = "Characteristic of monsoon-influenced regions with seasonal variability."
    else:
        water_mass = "mixed oceanic waters"
        climate_note = "Represents transitional oceanographic conditions."
    
    # Analyze thermocline strength
    if temp_gradient > 0.15:
        thermocline = "strong thermocline - rapid temperature decrease with depth indicates well-stratified waters, typical during warm seasons"
    elif temp_gradient > 0.08:
        thermocline = "moderate thermocline - gradual temperature change suggests seasonal mixing"
    else:
        thermocline = "weak thermocline - minimal temperature gradient may indicate recent mixing or winter conditions"
    
    # Salinity analysis
    if salinity_range > 0.5:
        salinity_note = "significant salinity variation suggests influence from freshwater input or different water masses"
    elif surface['salinity'] > 35.5:
        salinity_note = "high surface salinity indicates strong evaporation, typical of arid coastal regions"
    elif surface['salinity'] < 34.0:
        salinity_note = "lower salinity suggests freshwater influence from rivers or high precipitation"
    else:
        salinity_note = "typical oceanic salinity range indicates normal open-ocean conditions"
    
    # Biological implications
    if surface['temp'] > 22 and surface['salinity'] > 34:
        bio_note = "🐠 These warm, saline conditions support high marine productivity and diverse ecosystems."
    elif 15 < surface['temp'] < 22:
        bio_note = "🦈 Moderate temperatures create favorable conditions for temperate marine species."
    else:
        bio_note = "🐋 Cooler conditions typical of nutrient-rich upwelling zones that support large marine fauna."
    
    # Depth-specific insights
    oxygen_note = ""
    if len(depths) > 4:
        mid_depth_temp = depths[3]['temp']
        if mid_depth_temp < 10:
            oxygen_note = " The cooler mid-depth waters (around 70-90m) likely contain higher dissolved oxygen levels."
    
    # Location-specific context
    location_context = ""
    query_lower = query.lower()
    if "mumbai" in query_lower or "india" in query_lower:
        location_context = " This Arabian Sea location experiences strong monsoon influences, with seasonal temperature and salinity changes driven by southwest monsoon currents."
    elif "equator" in query_lower:
        location_context = " Equatorial waters show characteristic upwelling patterns and are influenced by trade wind dynamics."
    elif "pacific" in query_lower:
        location_context = " Pacific waters here may be influenced by ENSO patterns and show seasonal El Niño/La Niña effects."
    elif "arabian" in query_lower:
        location_context = " The Arabian Sea is known for intense seasonal productivity during monsoon upwelling periods."
    
    # Construct comprehensive analysis
    analysis = f"""🌊 **Oceanographic Analysis for {location_desc}**

**Water Mass Classification**: {water_mass.title()}
{climate_note}

**Temperature Profile**: Surface temperature of {surface['temp']}°C decreasing to {deep['temp']}°C at {deep['pres']}m depth shows a {thermocline}.

**Salinity Characteristics**: {surface['salinity']} PSU at surface - {salinity_note}.

**Vertical Structure**: The temperature gradient of {temp_gradient:.3f}°C/meter indicates {'strong stratification' if temp_gradient > 0.1 else 'moderate mixing'}.{oxygen_note}

{bio_note}

**Research Implications**: This profile suggests {'stable oceanographic conditions' if temp_gradient > 0.1 else 'active mixing processes'}, important for understanding {'thermal stratification and nutrient distribution' if temp_gradient > 0.1 else 'vertical mixing and ecosystem dynamics'}.

{location_context}

📊 **Key Metrics**: ΔT = {surface['temp'] - deep['temp']:.1f}°C, Salinity range = {salinity_range:.2f} PSU"""

    return analysis

@app.route("/query", methods=["POST", "OPTIONS"])
def handle_query():
    """Process oceanographic data queries"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})
        
    try:
        # Parse request
        data = request.get_json() or {}
        query = data.get("query", "ocean data")
        
        print(f"📊 Processing: {query}")
        
        # Location mapping - no external calls
        locations = {
            "mumbai": (19.0760, 72.8777),
            "india": (19.0760, 72.8777),  
            "equator": (0.0, 78.0),
            "pacific": (0.0, -140.0),
            "atlantic": (0.0, -30.0),
            "arabian": (15.0, 65.0),
            "indian ocean": (0.0, 78.0)
        }
        
        # Find location: place name or coordinates
        query_lower = query.lower()
        lat, lon = 0.0, 0.0
        location_desc = "in the ocean"

        coord = _parse_location_from_query(query_lower)
        if coord:
            lat, lon = coord
            location_desc = f"at {lat:.3f}°N, {lon:.3f}°E"
        else:
            for place, coords in locations.items():
                if place in query_lower:
                    lat, lon = coords
                    location_desc = f"near {place.title()}"
                    break
            else:
                # Random ocean location (deterministic per query)
                rng = _build_rng(0, 0, query_lower)
                lat = round(rng.uniform(-60, 60), 3)
                lon = round(rng.uniform(-180, 180), 3)
                location_desc = f"at {lat}°N, {lon}°E"
        
        # Generate realistic oceanographic depth profile
        rng = _build_rng(lat, lon, query_lower)
        depths = generate_realistic_profile(lat, lon, query_lower, rng)
        
        # Advanced AI analysis with real oceanographic insights
        explanation = generate_detailed_analysis(depths, location_desc, lat, lon, query)
        
        # Response format
        response = [{
            "profile_id": random.randint(1000, 9999),
            "lat": lat,
            "lon": lon,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "depth_levels": depths,
            "query_explain": explanation
        }]
        
        print(f"✅ Returning profile with {len(depths)} depth levels")
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"Query processing error: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route("/", methods=["GET"])
def health_check():
    """API health status"""
    return jsonify({
        "message": "FloatChat API is running! 🌊", 
        "status": "healthy",
        "version": "1.0"
    })

if __name__ == "__main__":
    print("🌊 FloatChat Oceanographic API")
    print("🚀 Starting server at http://localhost:5000")
    print("📊 Ready for ocean data queries!")
    print()
    
    # Start server
    app.run(
        host="127.0.0.1", 
        port=5000, 
        debug=False,
        threaded=True
    )