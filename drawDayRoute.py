
import json

def create_kml_from_summary(summary_path, kml_output_path):
    with open(summary_path, 'r') as f:
        data = json.load(f)

    kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>Ride Start Locations</name>
'''
    kml_footer = '</Document>\n</kml>'

    placemarks = []
    for idx, record in enumerate(data):
        fit_name = record.get('fitFileName', '')
        # Skip if this is a Part file but not Part_1
        if 'Part' in fit_name and 'Part_1' not in fit_name:
            continue
        lat = record.get('start_position_lat')
        lon = record.get('start_position_long')
        # Extract just the day number
        import re
        match = re.search(r'Day_(\d+)', fit_name)
        day_num = match.group(1) if match else fit_name
        if lat and lon:
            placemark = f'''    <Placemark>\n        <name>{day_num}</name>\n        <Point>\n            <coordinates>{lon},{lat},0</coordinates>\n        </Point>\n    </Placemark>\n'''
            placemarks.append(placemark)

    # Add the final 'End' placemark using the last record's end_position_lat/long
    if data:
        last = data[-1]
        end_lat = last.get('end_position_lat')
        end_lon = last.get('end_position_long')
        if end_lat and end_lon:
            end_placemark = f'''    <Placemark>\n        <name>End</name>\n        <Point>\n            <coordinates>{end_lon},{end_lat},0</coordinates>\n        </Point>\n    </Placemark>\n'''
            placemarks.append(end_placemark)

    with open(kml_output_path, 'w') as f:
        f.write(kml_header)
        for placemark in placemarks:
            f.write(placemark)
        f.write(kml_footer)

if __name__ == "__main__":
    create_kml_from_summary('summary.json', 'ride_start_locations.kml')
