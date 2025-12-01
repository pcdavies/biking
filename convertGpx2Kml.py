#!/usr/bin/env python3
"""
gpx_to_kml.py

Convert a GPX file to a KML file.

Usage:
    python gpx_to_kml.py --inputGpx my.gpx --outputKml my.kml
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify_xml(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def parse_gpx(gpx_path):
    tree = ET.parse(gpx_path)
    root = tree.getroot()

    ns = {}
    if "}" in root.tag:
        ns["gpx"] = root.tag.split("}")[0].strip("{")
    else:
        ns["gpx"] = ""

    def q(tag):
        return f"{{{ns['gpx']}}}{tag}" if ns["gpx"] else tag

    waypoints = []
    routes = []
    tracks = []

    # Waypoints
    for wpt in root.findall(q("wpt")):
        lat = wpt.attrib.get("lat")
        lon = wpt.attrib.get("lon")
        ele_elem = wpt.find(q("ele"))
        name_elem = wpt.find(q("name"))
        desc_elem = wpt.find(q("desc"))

        ele = ele_elem.text.strip() if ele_elem is not None and ele_elem.text else None
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Waypoint"
        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

        waypoints.append({"lat": lat, "lon": lon, "ele": ele, "name": name, "desc": desc})

    # Routes
    for rte in root.findall(q("rte")):
        name_elem = rte.find(q("name"))
        desc_elem = rte.find(q("desc"))
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Route"
        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

        points = []
        for rtept in rte.findall(q("rtept")):
            lat = rtept.attrib.get("lat")
            lon = rtept.attrib.get("lon")
            ele_elem = rtept.find(q("ele"))
            ele = ele_elem.text.strip() if ele_elem is not None and ele_elem.text else None
            points.append((lon, lat, ele))

        routes.append({"name": name, "desc": desc, "points": points})

    # Tracks
    for trk in root.findall(q("trk")):
        name_elem = trk.find(q("name"))
        desc_elem = trk.find(q("desc"))
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else "Track"
        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

        segments = []
        for trkseg in trk.findall(q("trkseg")):
            seg_points = []
            for trkpt in trkseg.findall(q("trkpt")):
                lat = trkpt.attrib.get("lat")
                lon = trkpt.attrib.get("lon")
                ele_elem = trkpt.find(q("ele"))
                ele = ele_elem.text.strip() if ele_elem is not None and ele_elem.text else None
                seg_points.append((lon, lat, ele))
            if seg_points:
                segments.append(seg_points)

        tracks.append({"name": name, "desc": desc, "segments": segments})

    return waypoints, routes, tracks


def build_kml(waypoints, routes, tracks, document_name="GPX to KML"):
    kml_ns = "http://www.opengis.net/kml/2.2"
    ET.register_namespace("", kml_ns)

    kml = ET.Element(f"{{{kml_ns}}}kml")
    doc = ET.SubElement(kml, "Document")

    name_elem = ET.SubElement(doc, "name")
    name_elem.text = document_name

    # Waypoints
    for w in waypoints:
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = w["name"]
        if w["desc"]:
            ET.SubElement(pm, "description").text = w["desc"]

        point = ET.SubElement(pm, "Point")
        coords = ET.SubElement(point, "coordinates")
        coords.text = (
            f"{w['lon']},{w['lat']},{w['ele']}" if w["ele"] else f"{w['lon']},{w['lat']}"
        )

    # Routes
    for r in routes:
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = r["name"]
        if r["desc"]:
            ET.SubElement(pm, "description").text = r["desc"]

        ls = ET.SubElement(pm, "LineString")
        ET.SubElement(ls, "tessellate").text = "1"
        coords = ET.SubElement(ls, "coordinates")

        coord_strings = [
            f"{lon},{lat},{ele}" if ele else f"{lon},{lat}"
            for lon, lat, ele in r["points"]
        ]
        coords.text = " ".join(coord_strings)

    # Tracks
    for t in tracks:
        for idx, seg in enumerate(t["segments"], start=1):
            pm = ET.SubElement(doc, "Placemark")

            seg_name = t["name"]
            if len(t["segments"]) > 1:
                seg_name += f" (Segment {idx})"

            ET.SubElement(pm, "name").text = seg_name
            if t["desc"]:
                ET.SubElement(pm, "description").text = t["desc"]

            ls = ET.SubElement(pm, "LineString")
            ET.SubElement(ls, "tessellate").text = "1"
            coords = ET.SubElement(ls, "coordinates")

            coord_strings = [
                f"{lon},{lat},{ele}" if ele else f"{lon},{lat}" for lon, lat, ele in seg
            ]
            coords.text = " ".join(coord_strings)

    return kml


def main():
    parser = argparse.ArgumentParser(description="Convert GPX to KML.")
    parser.add_argument("--inputGpx", default="input.gpx",
                        help="Input GPX file (default: input.gpx)")
    parser.add_argument("--outputKml", default="output.kml",
                        help="Output KML file (default: output.kml)")
    args, unknown = parser.parse_known_args()

    input_gpx = args.inputGpx
    output_kml = args.outputKml

    if not os.path.isfile(input_gpx):
        print(f"Error: input file not found: {input_gpx}")
        sys.exit(1)

    waypoints, routes, tracks = parse_gpx(input_gpx)
    doc_name = os.path.basename(input_gpx)

    kml_elem = build_kml(waypoints, routes, tracks, document_name=doc_name)
    kml_str = prettify_xml(kml_elem)

    with open(output_kml, "w", encoding="utf-8") as f:
        f.write(kml_str)

    print(f"Converted {input_gpx} → {output_kml}")


if __name__ == "__main__":
    main()