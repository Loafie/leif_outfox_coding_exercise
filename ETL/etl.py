import pandas as pd

# Load the CSV file
df = pd.read_csv('MUP_INP_RY24_P03_V10_DY22_PrvSvc.CSV', encoding='cp1252')


print("Length: ", len(df))
for e in df:
    print(e)

new_df = df[df['Rndrng_Prvdr_State_Abrvtn'] == 'NY'].copy()
print("New Length: ", len(new_df))


geo = pd.read_csv('georef-united-states-of-america-zc-point.csv', sep=';')

zips_to_geo = {}

for i in range(len(geo)):
    zips_to_geo[str(geo['Zip Code'][i])] = [float(geo['Geo Point'][i].split(',')[0]), float(geo['Geo Point'][i].split(',')[1])]
#print(zips_to_geo)
zips_to_geo['10802'] = zips_to_geo['10804']
zips_to_geo['14642'] = zips_to_geo['14624']
new_df['zip_lat'] = 0.0
new_df['zip_lon'] = 0.0
for i, r in new_df.iterrows():
    new_df.loc[i, 'zip_lat'] = (zips_to_geo[str(r['Rndrng_Prvdr_Zip5'])][0])
    new_df.loc[i, 'zip_lon'] = (zips_to_geo[str(r['Rndrng_Prvdr_Zip5'])][1])

renames = {}
for c in new_df:
    if c.__contains__("Rndrng_"):
        renames[c] = c.replace("Rndrng_","")
new_df = new_df.rename(columns=renames)
print(new_df.head())
new_df.to_csv('NY_sample_data.csv', index=False, encoding='utf-8')

zips = []
lats = []
lons = []
for g in zips_to_geo:
    zips.append(g)
    lats.append(zips_to_geo[g][0])
    lons.append(zips_to_geo[g][1])


zips_to_latlon = pd.DataFrame({"Zip": zips, "Lat": lats, "Lon": lons})
zips_to_latlon.to_csv('zips_to_latlon.csv', index=False, encoding='utf-8')