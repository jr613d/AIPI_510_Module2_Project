"""Workstream D spatial helper. Run with the ASTRA interpreter (shapely + pyproj, no pandas):

    /Users/jim/dukeaipi/510_Sourcing_Data/Module_1_Project/ASTRA/school-map/.venv/bin/python src/ws_d_spatial.py

Reads the ASTRA atlas (segments with ESWALK flags, dissolved elementary zones, the elementary
walk overlay, raw 2024 block-group geometry, ACS B25077 / B25003 extracts) and writes
results/ws_d/zone_geography_spatial.json. Everything is measured in EPSG:32617 (UTM 17N, metres)
after reprojecting from WGS84; areas are converted to square miles. Block groups are assigned to
the elementary zone that contains their centroid (full, unclipped Census geometry), and the share
of each block group's land that falls inside that zone is recorded so straddling is visible.
"""
import csv
import json
import sys
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

SQM_PER_SQMI = 2_589_988.110336
OUT_DIR = paths.RESULTS / "ws_d"
OUT_DIR.mkdir(parents=True, exist_ok=True)

_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32617", always_xy=True).transform


def utm(geom_json):
    """GeoJSON geometry (lon/lat) -> shapely geometry in UTM 17N metres, made valid."""
    g = shape(geom_json)
    if not g.is_valid:
        g = g.buffer(0)
    return transform(_to_utm, g)


def sqmi(geom):
    return geom.area / SQM_PER_SQMI


def read_acs(path, fields):
    out = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            geoid = row["GEO_ID"].split("US")[-1]
            out[geoid] = {f: int(row[f]) for f in fields}
    return out


def home_value(est, moe):
    """Apply the atlas's Census sentinel rules. Returns (value or None, note)."""
    if est == -666666666:
        return None, "no estimate"
    if est == 9999 and moe == -333333333:
        return None, "below $10,000 (bottom-coded)"
    return est, ""


def main():
    data = json.loads(paths.MAP_DATA.read_text())
    segments = data["segments"]["features"]
    zones_src = data["boundaries"]["elementary"]["features"]
    walk_overlay = utm(data["walks"]["elementary"]["features"][0]["geometry"])
    district = utm(data["district"]["features"][0]["geometry"])
    housing_raw = json.loads(paths.HOUSING_GEOJSON.read_text())["features"]
    b25077 = read_acs(paths.ACS_B25077, ["B25077_E001", "B25077_M001"])
    b25003 = read_acs(paths.ACS_B25003, ["B25003_E001", "B25003_E002", "B25003_E003"])
    schools = {s["name"]: s for s in data["schools"] if s["level"] == "elementary"}

    # Segments grouped by base elementary school (ENAME).
    by_zone = {}
    for f in segments:
        p = f["properties"]
        g = utm(f["geometry"])
        by_zone.setdefault(p["ENAME"], []).append({
            "segno": p.get("SEGNO"), "shortname": p.get("SHORTNAME"),
            "eswalk": p.get("ESWALK") == "Y", "geom": g, "area_sqmi": sqmi(g),
        })

    # Dissolved zone polygons from the atlas (same method as the segment union; we check both).
    zone_geoms = {}
    for f in zones_src:
        zone_geoms[f["properties"]["name"]] = {"geom": utm(f["geometry"]),
                                               "atlas_area": f["properties"]["area"],
                                               "atlas_segments": f["properties"]["segments"]}

    # Block groups: full geometry, centroid assignment.
    bgs = []
    for f in housing_raw:
        p = f["properties"]
        g = utm(f["geometry"])
        geoid = p["GEOID"]
        v = b25077.get(geoid)
        t = b25003.get(geoid)
        val, note = home_value(v["B25077_E001"], v["B25077_M001"]) if v else (None, "not in extract")
        bgs.append({
            "geoid": geoid, "tract": p["TRACT"], "blkgrp": p["BLKGRP"], "county": p["COUNTY"],
            "geom": g, "centroid": g.centroid, "area_sqmi": sqmi(g),
            "median_home_value": val, "moe": (v["B25077_M001"] if v and val is not None else None),
            "value_note": note,
            "households": t["B25003_E001"] if t else None,
            "owners": t["B25003_E002"] if t else None,
            "renters": t["B25003_E003"] if t else None,
            "in_district_share": round(g.intersection(district).area / g.area, 4) if g.area else 0,
        })

    zones_out = []
    bg_out = []
    assigned = set()
    for name, zinfo in sorted(zone_geoms.items()):
        zg = zinfo["geom"]
        segs = by_zone.get(name, [])
        seg_union = unary_union([s["geom"] for s in segs]) if segs else None
        walk_segs = [s for s in segs if s["eswalk"]]
        walk_union = unary_union([s["geom"] for s in walk_segs]) if walk_segs else None
        walk_area = sqmi(walk_union) if walk_union is not None else 0.0
        walk_overlay_area = sqmi(walk_overlay.intersection(zg))
        area = sqmi(zg)

        # Block groups by centroid; record straddle share.
        members = []
        touching = 0
        for bg in bgs:
            inter = bg["geom"].intersection(zg).area
            if inter > 0:
                touching += 1
            if zg.contains(bg["centroid"]):
                assigned.add(bg["geoid"])
                members.append(bg)
                bg_out.append({
                    "geoid": bg["geoid"], "county": bg["county"], "tract": bg["tract"], "blkgrp": bg["blkgrp"],
                    "zone": name.replace(" Elementary", ""),
                    "bg_area_sqmi": round(bg["area_sqmi"], 3),
                    "share_of_bg_inside_zone": round(inter / bg["geom"].area, 3) if bg["geom"].area else None,
                    "share_of_bg_inside_district": bg["in_district_share"],
                    "median_home_value": bg["median_home_value"], "moe": bg["moe"],
                    "moe_over_30pct": (bg["moe"] is not None and bg["median_home_value"]
                                       and bg["moe"] > 0.3 * bg["median_home_value"]),
                    "value_note": bg["value_note"],
                    "households": bg["households"], "owners": bg["owners"], "renters": bg["renters"],
                })
        vals = sorted(m["median_home_value"] for m in members if m["median_home_value"] is not None)
        hh = sum(m["households"] or 0 for m in members)
        rent = sum(m["renters"] or 0 for m in members)
        own = sum(m["owners"] or 0 for m in members)
        campus = schools.get(name, {}).get("location")
        zones_out.append({
            "zone": name.replace(" Elementary", ""),
            "area_sqmi": round(area, 2),
            "atlas_area_sqmi": zinfo["atlas_area"],
            "segment_union_area_sqmi": round(sqmi(seg_union), 2) if seg_union is not None else None,
            "n_segments": len(segs),
            "atlas_n_segments": zinfo["atlas_segments"],
            "n_walk_segments": len(walk_segs),
            "walk_segment_share": round(len(walk_segs) / len(segs), 3) if segs else None,
            "walk_area_sqmi": round(walk_area, 2),
            "walk_area_share": round(walk_area / area, 3) if area else None,
            "walk_overlay_area_share": round(walk_overlay_area / area, 3) if area else None,
            "largest_segment_sqmi": round(max(s["area_sqmi"] for s in segs), 2) if segs else None,
            "n_blockgroups_centroid": len(members),
            "n_blockgroups_touching": touching,
            "n_blockgroups_with_value": len(vals),
            "bg_value_min": vals[0] if vals else None,
            "bg_value_median": (vals[len(vals) // 2] if len(vals) % 2 else
                                (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2) if vals else None,
            "bg_value_max": vals[-1] if vals else None,
            "households": hh, "owners": own, "renters": rent,
            "renter_share": round(rent / hh, 3) if hh else None,
            "campus_lat": campus[0] if campus else None, "campus_lon": campus[1] if campus else None,
            "campus_inside_own_zone": (zg.contains(transform(_to_utm, shape({"type": "Point", "coordinates": [campus[1], campus[0]]})))
                                       if campus else None),
        })

    unassigned = [bg["geoid"] for bg in bgs if bg["geoid"] not in assigned]
    out = {
        "crs": "EPSG:32617 (UTM 17N) for measurement; inputs WGS84",
        "method": ("Zones are the atlas's dissolved ENAME segment unions. Block groups are full 2024 Census "
                   "geometry assigned by centroid; share_of_bg_inside_zone shows straddling. No zone-level "
                   "median is a true median: bg_value_median is the median of block-group medians."),
        "n_segments_total": len(segments),
        "n_walk_segments_total": sum(1 for f in segments if f["properties"].get("ESWALK") == "Y"),
        "district_area_sqmi": round(sqmi(district), 2),
        "walk_overlay_area_sqmi": round(sqmi(walk_overlay), 2),
        "n_blockgroups_raw": len(bgs),
        "n_blockgroups_assigned": len(assigned),
        "unassigned_blockgroups": unassigned,
        "zones": zones_out,
        "blockgroups": bg_out,
    }
    (OUT_DIR / "zone_geography_spatial.json").write_text(json.dumps(out, indent=1))
    for z in zones_out:
        print(f"{z['zone']:<14} area {z['area_sqmi']:>6} (atlas {z['atlas_area_sqmi']}) segs {z['n_segments']:>2} "
              f"walk {z['n_walk_segments']:>2} walk_area_share {z['walk_area_share']} "
              f"bgs {z['n_blockgroups_centroid']}/{z['n_blockgroups_touching']} "
              f"val {z['bg_value_min']}/{z['bg_value_median']}/{z['bg_value_max']} rent {z['renter_share']}")
    print("unassigned block groups:", len(unassigned))


if __name__ == "__main__":
    main()
