import decimal
import pandas as pd
import geopandas as gpd

data = pd.read_csv('data/ekv-2023_tpat_maa.csv', delimiter=';', encoding='latin1', low_memory=False)
helsinki = data[data['Kuntanro'] == "91"]

grouped = helsinki.groupby('Äänestysaluetunnus')['Äänet yhteensä lkm'].sum().reset_index()
grouped = grouped.rename(columns={'Äänet yhteensä lkm': 'Total Votes'})
helsinki = helsinki.merge(grouped, on='Äänestysaluetunnus', how='left')
helsinki["Osuus(%)"] = (helsinki['Äänet yhteensä lkm'] / helsinki['Total Votes'] * 100).round(decimals=2)

# Get top 5 parties for each district
top5 = (
    helsinki
    .sort_values(['Äänestysaluetunnus', 'Äänet yhteensä lkm'], ascending=[True, False])
    .groupby('Äänestysaluetunnus')
    .head(5)
)

# Pivot so each district is one row with 5 parties' info
top5 = top5.assign(rank=top5.groupby('Äänestysaluetunnus').cumcount() + 1)
top5_pivot = (
    top5.pivot(index='Äänestysaluetunnus', columns='rank', values=[
        'Puolueen/ryhmän nimilyhenne suomeksi', 'Puolueen/ryhmän nimi suomeksi', 'Äänet yhteensä lkm', 'Osuus(%)'
    ])
)
top5_pivot.columns = [f"{col[0]}_{col[1]}" for col in top5_pivot.columns]
top5_pivot = top5_pivot.reset_index()

# Download geometry
wfs_url = "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"
layer = "avoindata:Halke_aanestysalue"
gdf = gpd.read_file(
    f"{wfs_url}?service=WFS&version=2.0.0&request=GetFeature&typeName={layer}&outputFormat=application/json"
)

# Join geometry with top5
gdf['Äänestysaluetunnus'] = gdf['tunnus'].astype(str)
top5_pivot['Äänestysaluetunnus'] = top5_pivot['Äänestysaluetunnus'].astype(str)
gdf_small = gdf.merge(top5_pivot, on='Äänestysaluetunnus', how='left')
gdf_small = gdf_small.to_crs(epsg=4326)

# Save the smaller GeoJSON
gdf_small.to_file("data/helsinki_top5.geojson", driver="GeoJSON")