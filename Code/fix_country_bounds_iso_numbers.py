import os
import pandas as pd
import numpy as np
import rasterio
import glob
import subprocess
from pycountry import countries
#docker push kristinelister/basic-geo-python-docker:latest
#docker.io/kristinelister/basic-geo-python-docker:latest
#gcsfuse globagri-upload-bucket globagriexpansion/
#gcr.io/globagri/basic-geo-python-docker
#sudo umount ~/globagriexpansion/
#gsutil -m cp ExpansionRound1.py gs://globagri-upload-bucket/Code/

def convert_iso_num(data,iso_code_convert_list,out_code):
    try:
        iso_num_convert_list = [int(countries.get(alpha_3=x).numeric) for x in iso_code_convert_list]
    except:
        if out_code == 729:
            iso_num_convert_list = [728,729]
    print(iso_num_convert_list)
    data[np.isin(data,iso_num_convert_list)] = out_code
    return data


globagri_regions = ['CHN','SUN', 'BAL','YUG','SDN'];
SUN_iso_list = ['ARM', 'AZE', 'BLR', 'GEO', 'KAZ', 'KGZ', 'MDA', 'RUS', 'TJK', 'TKM', 'UKR', 'UZB'];
BAL_iso_list = ['BEL', 'LUX'];
# Note that Globagri has separate China regions, and SPAM has one CHN as aggregated entry
CHN_iso_list = ['CHN', 'TWN', 'HKG']
YUG_iso_list = ['BIH','HRV','MKD','MNE','SRB','SVN']
SDN_iso_list = ['SDN','SSN']

output_dir = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds'
country_bounds_f = '/Users/kristine/WRI/NationalGeographic/Phase2/Country_Bounds/CountryBounds.tif'
country_bounds_src = rasterio.open(country_bounds_f)
country_bounds_nodata = country_bounds_src.nodatavals[0]
data = country_bounds_src.read(1)

for region in globagri_regions:
    if region == 'CHN':
        iso_list = CHN_iso_list
        out_code = 156
    elif region == 'SUN':
        iso_list = SUN_iso_list
        out_code = 810
    elif region=='YUG':
        iso_list = YUG_iso_list
        out_code = 891
    elif region=='SDN':
        iso_list=SDN_iso_list
        out_code = 729
    else:
        iso_list = BAL_iso_list
        out_code = 56
    data = convert_iso_num(data,iso_list,out_code)
    

kwds = country_bounds_src.profile
out_local_file = os.path.join(output_dir,'GlobAgri_ISO.tif')

data[data<0] = 0
#data[data==10] = 0
print(np.unique(data))
iso_codes_df = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/FAO_country_codes_table.csv')
iso_codes_df = np.unique(iso_codes_df[iso_codes_df['UNI'].isin(np.unique(data).tolist())]['ISO3'].values).tolist()
print(iso_codes_df)
cropping_intensity = pd.read_csv('/Users/kristine/WRI/NationalGeographic/Phase2/Crop_Livestock/cropping_intensity_country_all_scenarios.csv')
cropping_intensity_iso = np.unique(cropping_intensity['ISO3'].values).tolist()
common = set(cropping_intensity_iso) & set(iso_codes_df)
different = [x for x in iso_codes_df+cropping_intensity_iso if x not in common]
print(len(common))
print(len(different))
print(different)
print(len(set(iso_codes_df)))
print(sorted(common))
with rasterio.open(out_local_file, 'w', **kwds) as dst_dataset:
    data = data.astype('Int16')
    dst_dataset.nodataval = 0
    dst_dataset.write_band(1,data)
    
