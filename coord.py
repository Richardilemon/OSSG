import geopandas as gpd
from shapely.geometry import Point

# Path to the shapefile
shapefile_path = 'path/to/shapefile.shp'

# Load the shapefile
gdf = gpd.read_file(shapefile_path)

# Coordinate to filter (e.g., latitude and longitude)
target_coordinate = (12.4924, 41.8902) 

# Create a Point geometry for the given coordinate
target_point = Point(target_coordinate)

# Filter rows where the geometry matches the specific point
# This assumes the shapefile contains points; modify as needed for polygons or other geometries.
filtered_data = gdf[gdf['geometry'] == target_point]

# Uncomment the next line if dealing with polygons
# filtered_data = gdf[gdf.contains(target_point)]

# Display filtered data
print(filtered_data)

# Convert to a regular DataFrame (if needed, dropping the geometry)
df = filtered_data.drop(columns='geometry')
print(df)
