from flask import Flask, request, render_template, jsonify
from shapely.geometry import Point
from pyproj import Transformer
import geopandas as gpd

app = Flask(__name__)

# Load shapefile once to save time
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.shp'
gdf = gpd.read_file(shapefile_path)

@app.route('/')
def index():
    return render_template('index.html')  # Render your HTML file

@app.route('/get_status', methods=['POST'])
def get_status():
    data = request.json
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
    else:
        return jsonify({"error": "Invalid coordinate type."}), 400

    # Transform Easting/Northing if needed
    if coordinate_type == 'EN':
        utm_zone = 31
        northern_hemisphere = True
        transformer = Transformer.from_proj(
            proj_from=f"+proj=utm +zone={utm_zone} +ellps=WGS84" + (" +south" if not northern_hemisphere else ""),
            proj_to="EPSG:4326"
        )
        coord_x, coord_y = transformer.transform(coord_x, coord_y)

    # Create a Point and filter shapefile data
    target_point = Point(coord_x, coord_y)
    filtered_data = gdf[gdf.contains(target_point)]

    if filtered_data.empty:
        return jsonify({"status": "No data found for the given coordinates."})
    
    return jsonify({"status": "Data found!", "details": filtered_data.to_dict()})

if __name__ == '__main__':
    app.run(debug=True)
