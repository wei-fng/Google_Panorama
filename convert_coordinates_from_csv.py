import pandas as pd
from pyproj import Transformer

source_crs = "EPSG:32650"

df = pd.read_csv("sample_points.csv", delimiter="\t")  # Input source CRS, e.g., EPSG:32650

df.columns = df.columns.str.strip()

df[['X', 'Y']] = df['X,Y'].str.split(',', expand=True)

df['X'] = df['X'].astype(float)
df['Y'] = df['Y'].astype(float)

print("Columns after splitting:", df.columns)
print("First few rows of the data after splitting:", df.head())

transformer = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)

df["longitude"], df["latitude"] = zip(*df.apply(lambda row: transformer.transform(row["X"], row["Y"]), axis=1))

df.to_csv("converted_points.txt", sep="\t", index=False)

print(df.head())
