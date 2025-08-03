
import os
import glob
from fit2gpx import Converter

fit_dir = './fitData'
gpx_dir = './gpxData'
os.makedirs(gpx_dir, exist_ok=True)

fit_files = glob.glob(os.path.join(fit_dir, '*.fit'))

for fit_file in fit_files:
    base_name = os.path.splitext(os.path.basename(fit_file))[0]
    gpx_file = os.path.join(gpx_dir, base_name + '.gpx')
    print(f"Converting {fit_file} -> {gpx_file}")
    try:
        converter = Converter(input_file_path=fit_file)
        converter.to_gpx(gpx_file)
    except Exception as e:
        print(f"Failed to convert {fit_file}: {e}")
