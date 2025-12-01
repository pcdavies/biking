#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET

def parse_kml_coordinates(coord_text):
    coords = []
    for line in coord_text.strip().split():
        parts = line.split(',')
        if len(parts) >= 2:
            lon, lat = float(parts[0]), float(parts[1])
            ele = float(parts[2]) if len(parts) > 2 else None
            coords.append((lat, lon, ele))
    return coords

def kml_to_gpx(input_kml, output_gpx):
    # Parse KML
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    tree = ET.parse(input_kml)
    root = tree.getroot()

    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "kml_to_gpx_python",
        "xmlns": "http://www.topografix.com/GPX/1/1"
    })

    # Process Placemarks
    for pm in root.findall(".//kml:Placemark", ns):
        name_el = pm.find("kml:name", ns)
        name = name_el.text if name_el is not None else "Unnamed"

        # Point → GPX waypoint
        point = pm.find(".//kml:Point/kml:coordinates", ns)
        if point is not None:
            coords = parse_kml_coordinates(point.text)
            if coords:
                lat, lon, ele = coords[0]
                wpt = ET.SubElement(gpx, "wpt", {"lat": str(lat), "lon": str(lon)})
                if ele is not None:
                    ET.SubElement(wpt, "ele").text = str(ele)
                ET.SubElement(wpt, "name").text = name
            continue

        # LineString → GPX track
        linestring = pm.find(".//kml:LineString/kml:coordinates", ns)
        if linestring is not None:
            coords = parse_kml_coordinates(linestring.text)
            trk = ET.SubElement(gpx, "trk")
            ET.SubElement(trk, "name").text = name
            trkseg = ET.SubElement(trk, "trkseg")

            for lat, lon, ele in coords:
                trkpt = ET.SubElement(trkseg, "trkpt", {"lat": str(lat), "lon": str(lon)})
                if ele is not None:
                    ET.SubElement(trkpt, "ele").text = str(ele)
            continue

    # Write GPX file
    ET.indent(gpx)
    ET.ElementTree(gpx).write(output_gpx, encoding="utf-8", xml_declaration=True)

def main():
    parser = argparse.ArgumentParser(description="Convert KML to GPX")
    parser.add_argument("--inputKml", help="Input KML file", default="us_ride_detail.kml")
    parser.add_argument("--outputGpx", help="Output GPX file", default="output.gpx")
    args, _ = parser.parse_known_args()   # Ignore any extra args

    kml_to_gpx(args.inputKml, args.outputGpx)

if __name__ == "__main__":
    main()