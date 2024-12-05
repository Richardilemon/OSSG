import geopandas as gpd

# Path to the shapefile
shapefile_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.shp'

# Load the shapefile into a GeoDataFrame
gdf = gpd.read_file(shapefile_path)

# Optional: If you want to drop the geometry column (which is specific to GeoDataFrame)
gdf = gdf.drop(columns='geometry')

# Path to the output CSV file
csv_path = '/mnt/c/Users/hp/Desktop/OSSG/GENERAL_ACQUISITION.csv'

# Write the GeoDataFrame to a CSV file
gdf.to_csv(csv_path, index=False)

# Confirm the export
print(f"CSV file saved at: {csv_path}")
