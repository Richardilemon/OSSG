from flask import Flask, request, render_template, jsonify
from shapely.geometry import Point
from pyproj import CRS, Proj, transform
import geopandas as gpd

app = Flask(__name__)

# Load shapefile and ensure CRS is UTM
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/LAGOS_EXCISION.shp'
gdf = gpd.read_file(shapefile_path)

# Specify the UTM zone and hemisphere for Easting/Northing
utm_zone = 31
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

    # Determine the type of coordinates and extract values
    coord_type = data.get('type')
    x = data.get('x')
    y = data.get('y')

    print(f"Coordinate Type: {coord_type}")
    print(f"x: {x} (type: {type(x)})")
    print(f"y: {y} (type: {type(y)})")

    if coord_type == 'LL':
        try:
            longitude = float(x)
            latitude = float(y)
            # Convert longitude/latitude to UTM
            proj_utm = Proj(utm_crs)
            easting, northing = proj_utm(longitude, latitude)
            print(f"Converted to UTM: Easting: {easting}, Northing: {northing}")
        except ValueError:
            return jsonify({"error": "Invalid longitude or latitude values"}), 400
    elif coord_type == 'EN':
        try:
            easting = float(x)
            northing = float(y)
            print(f"Using provided UTM coordinates: Easting: {easting}, Northing: {northing}")
        except ValueError:
            return jsonify({"error": "Invalid easting or northing values"}), 400
    else:
        return jsonify({"error": "Invalid input data"}), 400

    # Create a point and check if it is within any polygon in the GeoDataFrame
    point = Point(easting, northing)
    print(f"Point: {point}")

    # Filter shapefile data
    filtered_data = gdf[gdf.geometry.contains(point)]

    # Handle precision issues with a buffer
    if filtered_data.empty:
        buffered_point = point.buffer(1e-6)  # Small buffer in meters
        filtered_data = gdf[gdf.geometry.intersects(buffered_point)]

    if filtered_data.empty:
        return jsonify({"status": "No data found for the given coordinates."})

    # Convert geometries to WKT for serialization
    filtered_data = filtered_data.copy()
    filtered_data['geometry'] = filtered_data['geometry'].apply(lambda geom: geom.wkt)

    return jsonify(filtered_data.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)