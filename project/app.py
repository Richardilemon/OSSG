from flask import Flask, request, render_template, jsonify
from shapely.geometry import Point
from pyproj import CRS
import geopandas as gpd

app = Flask(__name__)

# Load shapefile and ensure CRS is UTM
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/LAGOS_EXCISION.shp'
gdf = gpd.read_file(shapefile_path)

# Specify the UTM zone and hemisphere for Easting/Northing
utm_zone = 31
northern_hemisphere = True
utm_crs = CRS.from_string(f"EPSG:326{utm_zone}")  # EPSG code for UTM zone 31N

# Reproject shapefile to UTM if not already in the same CRS
if gdf.crs != utm_crs:
    gdf = gdf.to_crs(utm_crs)
print(f"Shapefile CRS: {gdf.crs}")

@app.route('/')
def index():
    return render_template('index.html')  # Render your HTML file

@app.route('/get_status', methods=['POST'])
def get_status():
    data = request.json
    print(f"Received Data: {data}")

    # Get easting and northing from request
    try:
        easting = float(data.get('x'))
        northing = float(data.get('y'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid easting/northing values."}), 400

    # Create a Point geometry using easting and northing
    target_point = Point(easting, northing)
    print(f"Target Point: {target_point}")
    print(f"Shapefile Bounds: {gdf.total_bounds}")

    # Filter shapefile data
    filtered_data = gdf[gdf.geometry.contains(target_point)]

    # Handle precision issues with a buffer
    if filtered_data.empty:
        buffered_point = target_point.buffer(1e-6)  # Small buffer in meters
        filtered_data = gdf[gdf.geometry.intersects(buffered_point)]

    if filtered_data.empty:
        return jsonify({"status": "No data found for the given coordinates."})
    
    # Convert geometries to WKT for serialization
    filtered_data = filtered_data.copy()
    filtered_data['geometry'] = filtered_data['geometry'].apply(lambda geom: geom.wkt)

    # Return as JSON
    return jsonify({
        "status": "Data found!",
        "details": filtered_data.to_dict(orient='records')
    })

if __name__ == '__main__':
    app.run(debug=True)
