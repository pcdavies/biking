import os
import re
from fitparse import FitFile

def extract_day_number(filename):
    match = re.search(r'Day_(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

def main():
    test_dir = './test'
    out_file = 'allRoutes.fit'
    fit_files = [f for f in os.listdir(test_dir) if f.endswith('.fit')]
    fit_files.sort(key=extract_day_number)

    first = True
    merged_data = b''
    for fname in fit_files:
        fpath = os.path.join(test_dir, fname)
        print(f"reading file: {fname}")
        with open(fpath, 'rb') as f:
            file_bytes = f.read()
            if first:
                merged_data += file_bytes
                first = False
            else:
                # Skip the header (first 12 bytes + header size field)
                header_size = file_bytes[0]
                merged_data += file_bytes[header_size:]
        print(f"merged file: {fname}")

    if merged_data:
        with open(out_file, 'wb') as outf:
            outf.write(merged_data)
        print(f"merged file: {out_file}")
    else:
        print("No FIT files found to merge.")

if __name__ == "__main__":
    main()
