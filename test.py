from flask import Flask, request, render_template, jsonify
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd

app = Flask(__name__)

# Load shapefile once to save time
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.shp'
gdf = gpd.read_file(shapefile_path)

# Ensure CRS is WGS84
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")
print(f"Shapefile CRS: {gdf.crs}")

@app.route('/')
def index():
    return render_template('index.html')  # Render your HTML file

@app.route('/get_status', methods=['POST'])
def get_status():
    data = request.json
    print(f"Received Data: {data}")

    coordinate_type = data.get('type')
    coord_x = float(data.get('x'))
    coord_y = float(data.get('y'))

   
    # Validation
    if coordinate_type == 'LL':
        if not (-180 <= coord_x <= 180 and -90 <= coord_y <= 90):
            return jsonify({"error": "Invalid Longitude/Latitude values."}), 400
    elif coordinate_type == 'EN':
        if not (100000 <= coord_x <= 900000 and coord_y > 0):
            return jsonify({"error": "Invalid Easting/Northing values."}), 400
        # Transform Easting/Northing to WGS84
        utm_zone = 31
        northern_hemisphere = True
        transformer = Transformer.from_proj(
            proj_from=f"+proj=utm +zone={utm_zone} +ellps=WGS84" + (" +south" if not northern_hemisphere else ""),
            proj_to="EPSG:4326"
        )
        coord_x, coord_y = transformer.transform(coord_x, coord_y)
        print(f"Transformed Coordinates: Longitude={coord_x}, Latitude={coord_y}")
    else:
        return jsonify({"error": "Invalid coordinate type."}), 400

    # Create Point geometry
    target_point = Point(coord_x, coord_y)
    print(f"Target Point: {target_point}")
    print(f"Shapefile Bounds: {gdf.total_bounds}")

    # Filter shapefile data
    filtered_data = gdf[gdf.geometry.contains(target_point)]

    # Handle precision issues with a buffer
    if filtered_data.empty:
        buffered_point = target_point.buffer(1e-6)
        filtered_data = gdf[gdf.geometry.intersects(buffered_point)]

    if filtered_data.empty:
        return jsonify({"status": "No data found for the given coordinates."})
    
    return jsonify({"status": "Data found!", "details": filtered_data.to_dict()})

if __name__ == '__main__':
    app.run(debug=True)
