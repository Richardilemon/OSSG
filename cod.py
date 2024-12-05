import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Proj, transform

# Path to the shapefile
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.shp'

# Load the shapefile
gdf = gpd.read_file(shapefile_path)

# UTM coordinates to use as target points
utm_x, utm_y = 543946.149, 723063.687  # Example UTM coordinates
utm_zone = 31  # Example UTM Zone
northern_hemisphere = True  # Set to False for the southern hemisphere

# Define the UTM projection (same as the shapefile's CRS if it's UTM)
utm_crs = CRS.from_string(f"EPSG:326{utm_zone}")

# Define the UTM and WGS84 (longitude/latitude) projections
utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=not northern_hemisphere)
wgs84_proj = Proj(proj='latlong', ellps='WGS84')

# Convert UTM to longitude/latitude
lon, lat = transform(utm_proj, wgs84_proj, utm_x, utm_y)
print(f"Converted Coordinates: Longitude={lon}, Latitude={lat}")

# If the shapefile's CRS is None or different from UTM, set it to the UTM CRS
if gdf.crs is None:
    gdf.set_crs(utm_crs, allow_override=True, inplace=True)
elif gdf.crs != utm_crs:
    gdf = gdf.to_crs(utm_crs)

# Create the target point using the UTM coordinates
target_point = Point(utm_x, utm_y)

# Filter rows where the geometry contains the specific UTM point (useful for polygons)
filtered_data = gdf[gdf.geometry.contains(target_point)]

# Path to the output CSV file
csv_path = '/mnt/c/Users/hp/Desktop/OSSG/filtered.csv'
# Write the GeoDataFrame to a CSV file
filtered_data.to_csv(csv_path, index=False)

# Display filtered data
print(filtered_data)

# Convert to a regular DataFrame (if needed, dropping the geometry)
df = filtered_data.drop(columns='geometry')
# Path to the output CSV file
csv_path = '/mnt/c/Users/hp/Desktop/OSSG/df.csv'
# Write the GeoDataFrame to a CSV file
df.to_csv(csv_path, index=False)
print(df)
