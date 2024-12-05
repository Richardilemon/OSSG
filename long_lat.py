import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform

# Path to the shapefile
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.shp'

# Load the shapefile
gdf = gpd.read_file(shapefile_path)

# UTM coordinates to convert
utm_x, utm_y = 543946.149, 723063.687  # Example UTM coordinates
utm_zone = 31  # Example UTM Zone
northern_hemisphere = True  # Set to False for the southern hemisphere

# Define the UTM and WGS84 (longitude/latitude) projections
utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=not northern_hemisphere)
wgs84_proj = Proj(proj='latlong', ellps='WGS84')

# Convert UTM to longitude/latitude
lon, lat = transform(utm_proj, wgs84_proj, utm_x, utm_y)
print(f"Converted Coordinates: Longitude={lon}, Latitude={lat}")

# Create a Point geometry for the converted coordinates
target_point = Point(lon, lat)

# Filter rows where the geometry matches the specific point
# This assumes the shapefile contains points; modify as needed for polygons or other geometries.
filtered_data = gdf[gdf['geometry'] == target_point]

# If you want to find features containing the point (useful for polygons)
# Uncomment the next line if dealing with polygons
filtered_data = gdf[gdf.contains(target_point)]

# Display filtered data
print(filtered_data)

# Convert to a regular DataFrame (if needed, dropping the geometry)
df = filtered_data.drop(columns='geometry')
print(df)
