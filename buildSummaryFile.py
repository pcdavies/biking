import os
import re
import sys
import glob
from fitparse import FitFile

def print_summary_fields(fit_file, summary_json=None):
    fitfile = FitFile(fit_file)
    fitfile_name = os.path.basename(fit_file)
    print(f"\nFile: {os.path.basename(fit_file)}")
    summary = {}
    # Collect summary fields from activity, session, and file_id messages
    for msg_type in ['activity', 'session', 'file_id']:
        for msg in fitfile.get_messages(msg_type):
            for field in msg:
                summary[field.name] = field.value
    # Find ending lat/long from last record
    end_lat = None
    end_long = None
    for record in fitfile.get_messages('record'):
        lat = None
        lon = None
        for field in record:
            if field.name == 'position_lat':
                lat = field.value
            elif field.name == 'position_long':
                lon = field.value
        if lat is not None and lon is not None:
            end_lat = lat
            end_long = lon

    # Print summary fields
    if summary:
        summary_record = {'fitFileName': fitfile_name}
        for k, v in summary.items():
            if k in [
                'max_temperature', 
                'min_temperature',
                'avg_temperature',
                'total_distance',
                'total_ascent',
                'total_descent',
                'total_calories',
                'total_eplasped_time',
                'enhanced_elapsed_time',
                'enhanced_avg_speed',
                'enhanced_max_speed',
                'avg_speed',
                'max_speed',
                "start_position_lat",
                "start_position_long",]:
                if "speed" in k:
                    v = v * 2.23694
                elif "temp" in k:
                    v = v * 1.8 + 32
                elif "ascent" in k or "descent" in k:
                    v = v * 3.28084
                elif "distance" in k:
                    v = v / 1609.34
                elif "start_position" in k:
                    v = v * (180.0 / 2147483648.0)  # Convert to degrees

                if isinstance(v, (float)):
                    if k in ("start_position_lat", "start_position_long"):
                        v = f"{v:.6f}"
                    else:
                        v = f"{v:.2f}"
                elif isinstance(v, (int)):
                    v = f"{v}"
                print(f"{k}: {v}")
                summary_record.update({k: v})
        # Print ending lat/long if found
        if end_lat is not None and end_long is not None:
            end_lat_deg = end_lat * (180.0 / 2147483648.0)
            end_long_deg = end_long * (180.0 / 2147483648.0)
            print(f"end_position_lat: {end_lat_deg:.6f}")
            print(f"end_position_long: {end_long_deg:.6f}")
            summary_record.update({
                "end_position_lat": f"{end_lat_deg:.6f}",
                "end_position_long": f"{end_long_deg:.6f}"
            })
        if summary_json is not None:
            summary_json.append(summary_record)
    else:
        print("No summary fields found.")


def extract_day_number(filename):
    match = re.search(r'Day_(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

def get_fit_files(directory):
    files = glob.glob(os.path.join(directory, '*.fit'))
    files.sort(key=extract_day_number)
    return files

def list_all_fields(fit_file):
    fitfile = FitFile(fit_file)
    fields = set()
    for record in fitfile.get_messages('record'):
        for field in record:
            fields.add(field.name)
    return sorted(fields)


def print_total_fields(fit_file, field_names):
    fitfile = FitFile(fit_file)
    print(f"File: {os.path.basename(fit_file)}")
    totals = {field: 0.0 for field in field_names}
    timestamps = []
    elapsed_times = []
    for record in fitfile.get_messages('record'):
        for field in record:
            if field.name in field_names and field.value is not None:
                try:
                    totals[field.name] += float(field.value)
                except Exception:
                    pass
            if field.name == 'timestamp' and field.value is not None:
                timestamps.append(field.value)
            if field.name == 'enhanced_elapsed_time' and field.value is not None:
                elapsed_times.append(float(field.value))
    # Special handling for distance: FIT files usually store distance in meters, but only the last record is the total distance
    if 'distance' in field_names:
        last_distance = None
        for record in fitfile.get_messages('record'):
            for field in record:
                if field.name == 'distance' and field.value is not None:
                    last_distance = field.value
        if last_distance is not None:
            # Convert meters to miles
            totals['distance'] = last_distance * 0.000621371
    # Special handling for duration and elapsed_time
    if 'duration' in field_names:
        if timestamps:
            duration_sec = (max(timestamps) - min(timestamps)).total_seconds()
            totals['duration'] = duration_sec
        else:
            totals['duration'] = 0.0
    if 'elapsed_time' in field_names:
        if elapsed_times:
            totals['elapsed_time'] = max(elapsed_times)
        elif timestamps:
            totals['elapsed_time'] = (max(timestamps) - min(timestamps)).total_seconds()
        else:
            totals['elapsed_time'] = 0.0
    # Print totals
    row = []
    for field in field_names:
        if field == 'distance':
            row.append(f"{field}: {totals[field]:.2f} miles")
        elif field in ('duration', 'elapsed_time'):
            # Print as H:MM:SS
            seconds = int(totals[field])
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            row.append(f"{field}: {h}:{m:02d}:{s:02d}")
        else:
            row.append(f"{field}: {totals[field]}")
    print(", ".join(row))

def print_selected_fields(fit_file, field_names):
    fitfile = FitFile(fit_file)
    print(f"\nFile: {os.path.basename(fit_file)}")
    for record in fitfile.get_messages('record'):
        row = []
        for field_name in field_names:
            value = None
            for field in record:
                if field.name == field_name:
                    value = field.value
                    break
            row.append(str(value) if value is not None else "N/A")
        print(", ".join(row))


def main():
    fit_dir = './fitData'
    fit_files = get_fit_files(fit_dir)

    summary_json = []
    for fit_file in fit_files:
        print_summary_fields(fit_file, summary_json)
    # write summary to a JSON file
    summary_file = os.path.join('./', 'summary.json')
    with open(summary_file, 'w') as f:
        import json
        json.dump(summary_json, f, indent=4)
    print(f"Summary written to {summary_file}")

if __name__ == "__main__":
    main()
