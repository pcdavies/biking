from fitparse import FitFile

def semicircles_to_degrees(semicircles):
    """Convert Garmin FIT semicircles to degrees."""
    return semicircles * (180.0 / 2**31)

def extract_lat_lon(fit_filename):
    fitfile = FitFile(fit_filename)
    coordinates = []

    for record in fitfile.get_messages('record'):
        lat = None
        lon = None
        temperature = None
        timestamp = None
        for field in record:
            if field.name == 'position_lat':
                lat = semicircles_to_degrees(field.value)
            elif field.name == 'position_long':
                lon = semicircles_to_degrees(field.value)
            elif field.name == 'temperature':
                # Convert Celsius to Fahrenheit if temperature is not None
                if field.value is not None:
                    temperature = field.value * 9.0 / 5.0 + 32.0
                else:
                    temperature = None
            elif field.name == 'timestamp':
                timestamp = field.value

        if lat is not None and lon is not None:
            coordinates.append((lat, lon, temperature, timestamp))

    return coordinates

if __name__ == "__main__":
    fit_file_path = "./data/Riding_across_the_US_Day_01_started_Garmin_late.fit"  # Replace with your actual file

    coords = extract_lat_lon(fit_file_path)

    for i, (lat, lon, temperature, timestamp) in enumerate(coords):
        temp_str = f"{temperature:.1f}°F" if temperature is not None else "N/A"
        print(f"{i + 1}: Latitude: {lat:.6f}, Longitude: {lon:.6f}, Temperature: {temp_str}, Timestamp: {timestamp}")

    # Print available field names in the FIT file (from the first 'record' message)
    fitfile = FitFile(fit_file_path)
    # first_record = next(fitfile.get_messages('record'), None)
    # if first_record:
    #     field_names = [field.name for field in first_record]
    #     print("\nAvailable fields in the first 'record' message:")
    #     for name in field_names:
    #         print(f"- {name}")
    # else:
    #     print("No 'record' messages found in the FIT file.")