import os
import re
from fitparse import FitFile
import simplekml
from datetime import timedelta

def extract_order_key(filename):
    # Handles Day_XX[_Part_Y].fit robustly
    base = os.path.basename(filename)
    # Accept both .fit and .FIT
    match = re.match(r"Day_(\d+)(?:_Part_(\d+))?\.fit$", base, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        part = int(match.group(2)) if match.group(2) else 0
        return (day, part)
    return (float('inf'), float('inf'))

def fit_files_in_order(fit_dir):
    files = [os.path.join(fit_dir, f) for f in os.listdir(fit_dir) if f.endswith('.fit')]
    files.sort(key=extract_order_key)
    return files

def fit_latlon_every_n_minutes(fitfile, minutes=10):
    points = []
    last_time = None
    for record in fitfile.get_messages('record'):
        lat = None
        lon = None
        timestamp = None
        for field in record:
            if field.name == 'position_lat':
                lat = field.value
            elif field.name == 'position_long':
                lon = field.value
            elif field.name == 'timestamp':
                timestamp = field.value
        if lat is not None and lon is not None and timestamp is not None:
            # Convert semicircles to degrees
            lat_deg = lat * (180.0 / 2147483648.0)
            lon_deg = lon * (180.0 / 2147483648.0)
            if last_time is None or (timestamp - last_time) >= timedelta(minutes=minutes):
                points.append((lat_deg, lon_deg))
                last_time = timestamp
    return points

def main():
    fit_dir = './fitData'
    out_kml = 'us_ride_detail.kml'
    files = fit_files_in_order(fit_dir)
    print("Sorted order:")
    for f in files:
        print(f)
    kml = simplekml.Kml()
    all_points = []
    for fit_path in files:
        print(f"Processing {fit_path}")
        try:
            fitfile = FitFile(fit_path)
            points = fit_latlon_every_n_minutes(fitfile, minutes=10)
            all_points.extend(points)
        except Exception as e:
            print(f"Failed to process {fit_path}: {e}")
    if all_points:
        ls = kml.newlinestring(name="US Ride Detail", coords=[(lon, lat) for lat, lon in all_points])
        ls.style.linestyle.width = 4
        ls.style.linestyle.color = simplekml.Color.red
        kml.save(out_kml)
        print(f"KML file written to {out_kml}")
    else:
        print("No points found.")

if __name__ == "__main__":
    main()
