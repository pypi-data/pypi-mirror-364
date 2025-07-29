import os
import re
import glob
import datetime
import pytz
import numpy as np
import pandas as pd
import netCDF4 as nc
import xarray as xr
import shutil
from netCDF4 import Dataset, date2num
from datetime import timedelta
from osgeo import gdal, ogr, osr
from shapely.geometry import box
from timezonefinder import TimezoneFinder
from tqdm import tqdm
import shutil
gdal.UseExceptions()

# =============================================================================
# Function to check that all raster files have matching dimensions, pixel size, and CRS.
# =============================================================================
def check_rasters(files):
    """
    Check that all provided raster files have matching dimensions, pixel size, and CRS.

    Parameters:
        files (list): List of raster file paths.

    Returns:
        bool: True if all checks pass, raises ValueError/FileNotFoundError otherwise.
    """
    if not files:
        raise ValueError("No raster files provided.")

    ref_file = files[0]
    ds = gdal.Open(ref_file)
    if ds is None:
        raise FileNotFoundError(f"Could not open {ref_file}")
    ref_width = ds.RasterXSize
    ref_height = ds.RasterYSize
    ref_gt = ds.GetGeoTransform()  # (originX, pixelWidth, rot, originY, rot, pixelHeight)
    ref_pixel_width = ref_gt[1]
    ref_pixel_height = ref_gt[5]  # typically negative
    ref_crs = ds.GetProjection()
    ds = None

    for f in files[1:]:
        ds = gdal.Open(f)
        if ds is None:
            raise FileNotFoundError(f"Could not open {f}")
        if ds.RasterXSize != ref_width or ds.RasterYSize != ref_height:
            raise ValueError("Error: Raster dimensions do not match.")
        gt = ds.GetGeoTransform()
        pixel_width = gt[1]
        pixel_height = gt[5]
        if pixel_width != ref_pixel_width or pixel_height != ref_pixel_height:
            raise ValueError("Error: Pixel sizes do not match.")
        if ds.GetProjection() != ref_crs:
            raise ValueError("Error: CRS does not match.")
        ds = None

    return True

# =============================================================================
# Function to tile a raster file into smaller chunks.
# =============================================================================
def create_tiles(infile, tilesize, overlap, tile_type):
    """
    Tile a raster file into smaller chunks.

    Parameters:
        infile (str): Path to input raster.
        tilesize (int): Size of each tile in pixels.
        overlap (int): Number of pixels to overlap between tiles.
        tile_type (str): Label to use for naming output tiles.

    Raises:
        FileNotFoundError: If the input file is not found.
        ValueError: If the overlap is not within the valid range.
    """
    ds = gdal.Open(infile)

    if overlap < 0 or overlap >= tilesize:
        raise ValueError("overlap must be 0 ≤ overlap < tilesize")
    
    if ds is None:
        raise FileNotFoundError(f"Could not open {infile}")

    width = ds.RasterXSize
    height = ds.RasterYSize

    out_folder = os.path.join(os.path.dirname(infile), tile_type)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    else:
        shutil.rmtree(out_folder)
        os.makedirs(out_folder)

    if tilesize >= width and tilesize >= height:
        outfile = os.path.join(out_folder, f"{tile_type}_0_0.tif")
        options = gdal.TranslateOptions(format='GTiff', srcWin=[0, 0, width, height])
        gdal.Translate(outfile, ds, options=options)
        print(f"Created single tile (original file): {outfile}")
        ds = None
        return

    for i in range(0, width, tilesize):
        for j in range(0, height, tilesize):
            tile_width = min(tilesize + overlap, width - i)
            tile_height = min(tilesize + overlap, height - j)
            outfile = os.path.join(out_folder, f"{tile_type}_{i}_{j}.tif")
            options = gdal.TranslateOptions(format='GTiff', srcWin=[i, j, tile_width, tile_height])
            gdal.Translate(outfile, ds, options=options)
            print(f"Created tile: {outfile}")
   
    ds = None

# =============================================================================
# The function expects two files in folder_path:
#        - 'data_stream-oper_stepType-instant.nc'
#        - "data_stream-oper_stepType-accum.n"
        
# It processes the data to compute temperature (in °C), surface pressure (in kPa), 
# relative humidity (in %), wind speed (in m/s), shortwave and longwave radiation (in W/m^2),
# and writes the results to a new netCDF file. This netCDF files will be used to create the 
# meteogrological forcing for SOLWEIG. Note that RAIN is set to 0.
# =============================================================================

def process_era5_data(start_time, end_time, folder_path, output_file="Outfile.nc"):
    """
    Process ERA5 NetCDF files to create meteorological forcing data for SOLWEIG.

    Parameters:
        start_time (str): Start datetime string in format "%Y-%m-%d %H:%M:%S".
        end_time (str): End datetime string in format "%Y-%m-%d %H:%M:%S".
        folder_path (str): Path containing ERA5 NetCDF files.
        output_file (str): Output NetCDF file name.
    """
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    def saturation_vapor_pressure(T):
        """
        Calculate saturation vapor pressure (in hPa) given temperature T in Celsius.
        """
        return 6.112 * np.exp((17.67 * T) / (T + 243.5))
    
    instant_file = os.path.join(folder_path, 'data_stream-oper_stepType-instant.nc')
    accum_file   = os.path.join(folder_path, 'data_stream-oper_stepType-accum.nc')
    
    ds_instant = xr.open_dataset(instant_file)
    ds_accum   = xr.open_dataset(accum_file)
    
    # Generate the correct time array using the provided start and end times (1-hour frequency)
    time_array = [start_time + timedelta(hours=i) 
                  for i in range(int((end_time - start_time).total_seconds() // 3600) + 1)]
    
    temperatures = ds_instant['t2m'].values
    dew_points   = ds_instant['d2m'].values
    
    surface_pressures = ds_instant['sp'].values 
    
    u10 = ds_instant['u10'].values
    v10 = ds_instant['v10'].values
    wind_speeds = np.sqrt(u10**2 + v10**2)
    
    # Convert from J m^-2 (accumulated over 3 hours) to W m^-2 by dividing by 3600.
    shortwave_radiation = ds_accum['ssrd'].values / 3600.0
    longwave_radiation  = ds_accum['strd'].values / 3600.0
    
    # Compute relative humidity (in %)
    e_temp      = saturation_vapor_pressure(temperatures - 273.15)
    e_dew_point = saturation_vapor_pressure(dew_points - 273.15)
    relative_humidities = 100.0 * (e_dew_point / e_temp)
    
    latitudes = ds_instant['latitude'].values
    longitudes = ds_instant['longitude'].values
    
    if latitudes.ndim == 1 and longitudes.ndim == 1:
        lon2d, lat2d = np.meshgrid(longitudes, latitudes)
    else:
        lat2d = latitudes
        lon2d = longitudes
    
    # Define the output NetCDF file
    with Dataset(output_file, 'w', format='NETCDF4') as nc:
        nc.createDimension('time', len(time_array))
        nc.createDimension('lat', lat2d.shape[0])
        nc.createDimension('lon', lon2d.shape[1])
        
        time_var = nc.createVariable('time', 'f8', ('time',))
        lat_var  = nc.createVariable('lat', 'f4', ('lat', 'lon'))
        lon_var  = nc.createVariable('lon', 'f4', ('lat', 'lon'))
        
        t2_var    = nc.createVariable('T2', 'f4', ('time', 'lat', 'lon'), zlib=True)
        psfc_var  = nc.createVariable('PSFC', 'f4', ('time', 'lat', 'lon'), zlib=True)
        rh2_var   = nc.createVariable('RH2', 'f4', ('time', 'lat', 'lon'), zlib=True)
        wind_var  = nc.createVariable('WIND', 'f4', ('time', 'lat', 'lon'), zlib=True)
        swdown_var= nc.createVariable('SWDOWN', 'f4', ('time', 'lat', 'lon'), zlib=True)
       # glw_var   = nc.createVariable('GLW', 'f4', ('time', 'lat', 'lon'), zlib=True)
        
        # The time units are defined relative to the start time.
        time_var.units = "hours since 1970-01-01 00:00:00"
        time_var.calendar = "gregorian"
        lat_var.units = "degrees_north"
        lon_var.units = "degrees_east"
        
        t2_var.units = "degC"
        psfc_var.units = "kPa"
        rh2_var.units = "%"
        wind_var.units = "m/s"
        swdown_var.units = "W/m^2"
       # glw_var.units = "W/m^2"
        
        time_var[:] = date2num(time_array, units=time_var.units, calendar=time_var.calendar)
        lat_var[:, :] = lat2d
        lon_var[:, :] = lon2d
        
        t2_var[:, :, :]    = temperatures
        psfc_var[:, :, :]  = surface_pressures
        rh2_var[:, :, :]   = relative_humidities
        wind_var[:, :, :]  = wind_speeds
        swdown_var[:, :, :] = shortwave_radiation
        #glw_var[:, :, :]    = longwave_radiation

    print("ERA5 forcing file created:", output_file)

# =============================================================================
#    The function will:
#        - Populate the list of available WRF output files (names starting with 'wrfout')
#          and sort them based on the datetime string embedded in the filename.
#        - Loop over the sorted files and extract variables:
#            - 2-meter temperature (T2)
#            - Mixing ratio at 2 m (Q2)
#            - Surface pressure (PSFC)
#            - Land surface temperature (TSK)
#            - Downwelling shortwave radiation (SWDOWN)
#            - Downwelling longwave radiation (GLW)
#            - U and V wind components (U10, V10) to compute wind speed
#        - Calculate relative humidity using a helper function.
#        - Generate an hourly time array between start_time and end_time.
#        - Combine the data from all files along the time axis and save to a new NetCDF file.
# =============================================================================

def process_wrfout_data(start_time, end_time, folder_path, output_file="Outfile.nc"):
    """
    Process WRF output files to create meteorological forcing data.

    Parameters:
        start_time (str): Start datetime string in format "%Y-%m-%d %H:%M:%S".
        end_time (str): End datetime string in format "%Y-%m-%d %H:%M:%S".
        folder_path (str): Directory containing wrfout files.
        output_file (str): Output NetCDF file name.
    """
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    def calculate_rh(t2, q2, psfc):
        # Compute saturation vapor pressure (in hPa) using temperature converted to Celsius.
        e_s = 6.112 * np.exp((17.67 * (t2 - 273.15)) / ((t2 - 273.15) + 243.5))
        e_s = e_s * 100  # convert hPa to Pa
        # Calculate actual vapor pressure using mixing ratio.
        Rd = 287.05  # Gas constant for dry air (J/kg/K)
        Rv = 461.5   # Gas constant for water vapor (J/kg/K)
        eps = Rd / Rv
        e = q2 * psfc / (eps + q2)
        rh = (e / e_s) * 100
        return np.clip(rh, 0, 100)
    
    # List and sort the WRF output files from the folder.
    # Files are assumed to be named like: "wrfout_d03_YYYY-MM-DD_HH:MM:SS"
    all_files = os.listdir(folder_path)
    wrf_files = [f for f in all_files if f.startswith("wrfout")]
    
    # Define a helper to extract datetime from the filename.
    def extract_datetime(filename):
        # Use regex to extract the date/time part.
        # The expected format is something like: wrfout_d03_2020-08-12_18:00:00
        match = re.search(r"wrfout_\w+_(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})", filename)
        if match:
            dt_str = match.group(1)
            return datetime.datetime.strptime(dt_str, "%Y-%m-%d_%H:%M:%S")
        else:
            # If not matched, return a very early date to push it to the beginning.
            return datetime.datetime.min

    # Sort the file list based on the extracted datetime.
    wrf_files_sorted = sorted(wrf_files, key=extract_datetime)
    
    # Generate the time array for the simulation period (hourly frequency)
    total_hours = int((end_time - start_time).total_seconds() // 3600) + 1
    time_array = [start_time + timedelta(hours=i) for i in range(total_hours)]
    
    t2_list, wind_list, rh2_list, tsk_list = [], [], [], []
    swdown_list, glw_list, psfc_list = [], [], []
    lat, lon = None, None
    
    for file in wrf_files_sorted:
        file_path = os.path.join(folder_path, file)
        with xr.open_dataset(file_path) as ds:
            # Extract variables.
            t2 = ds['T2'].values           # 2-meter temperature (K)
            q2 = ds['Q2'].values           # Mixing ratio at 2 m (kg/kg)
            psfc = ds['PSFC'].values       # Surface pressure (Pa)
            
            t2_list.append(t2)
            tsk_list.append(ds['TSK'].values)       # Land surface temperature (K)
            swdown_list.append(ds['SWDOWN'].values)    # Downwelling shortwave radiation (W/m^2)
            #glw_list.append(ds['GLW'].values)          # Downwelling longwave radiation (W/m^2)
            psfc_list.append(psfc)
            
            # Calculate wind speed from U10 and V10 components at 10 m.
            u10 = ds['U10'].values
            v10 = ds['V10'].values
            wind_speed = np.sqrt(u10**2 + v10**2)
            wind_list.append(wind_speed)
            
            # Calculate relative humidity using the helper function.
            rh2 = calculate_rh(t2, q2, psfc)
            rh2_list.append(rh2)
            
            # Extract latitude and longitude (assumed same for all files).
            if lat is None or lon is None:
                lat = ds['XLAT'].values[0, :, :]
                lon = ds['XLONG'].values[0, :, :]
    
    t2_array      = np.concatenate(t2_list, axis=0)
    wind_array    = np.concatenate(wind_list, axis=0)
    rh2_array     = np.concatenate(rh2_list, axis=0)
    tsk_array     = np.concatenate(tsk_list, axis=0)
    swdown_array  = np.concatenate(swdown_list, axis=0)
    #glw_array     = np.concatenate(glw_list, axis=0)
    psfc_array    = np.concatenate(psfc_list, axis=0)
    
    # Create a new NetCDF file and write the combined data.
    with Dataset(output_file, 'w', format='NETCDF4') as nc:
        nc.createDimension('time', len(time_array))
        nc.createDimension('lat', lat.shape[0])
        nc.createDimension('lon', lon.shape[1])
        
        time_var = nc.createVariable('time', 'f8', ('time',))
        lat_var = nc.createVariable('lat', 'f4', ('lat', 'lon'))
        lon_var = nc.createVariable('lon', 'f4', ('lat', 'lon'))
        
        t2_var    = nc.createVariable('T2', 'f4', ('time', 'lat', 'lon'), zlib=True)
        wind_var  = nc.createVariable('WIND', 'f4', ('time', 'lat', 'lon'), zlib=True)
        rh2_var   = nc.createVariable('RH2', 'f4', ('time', 'lat', 'lon'), zlib=True)
        tsk_var   = nc.createVariable('TSK', 'f4', ('time', 'lat', 'lon'), zlib=True)
        swdown_var= nc.createVariable('SWDOWN', 'f4', ('time', 'lat', 'lon'), zlib=True)
     #   glw_var   = nc.createVariable('GLW', 'f4', ('time', 'lat', 'lon'), zlib=True)
        psfc_var  = nc.createVariable('PSFC', 'f4', ('time', 'lat', 'lon'), zlib=True)
        
        time_var.units = "hours since 1970-01-01 00:00:00"
        time_var.calendar = "gregorian"
        lat_var.units = "degrees_north"
        lon_var.units = "degrees_east"
        
        t2_var.units = "K"
        wind_var.units = "m/s"
        rh2_var.units = "%"
        tsk_var.units = "K"
        swdown_var.units = "W/m^2"
       # glw_var.units = "W/m^2"
        psfc_var.units = "Pa"
        
        time_var[:] = date2num(time_array, units=time_var.units, calendar=time_var.calendar)
        lat_var[:, :] = lat
        lon_var[:, :] = lon
        
        t2_var[:, :, :]    = t2_array
        wind_var[:, :, :]  = wind_array
        rh2_var[:, :, :]   = rh2_array
        tsk_var[:, :, :]   = tsk_array
        swdown_var[:, :, :] = swdown_array
        #glw_var[:, :, :]    = glw_array
        psfc_var[:, :, :]   = psfc_array
    
    print(f"New NetCDF file created: {output_file}")
    
# =============================================================================
# Function to process the NetCDF file and create metfiles based on a set of raster tiles.
# =============================================================================
def process_metfiles(netcdf_file, raster_folder, base_path, selected_date_str):
    """
    Extract meteorological variables from a NetCDF file for each raster tile and write formatted metfiles.

    Parameters:
        netcdf_file (str): Path to processed NetCDF file.
        raster_folder (str): Path to raster tiles (e.g., DEM tiles).
        base_path (str): Base directory for output.
        selected_date_str (str): Date string (YYYY-MM-DD) for which to extract data.
    """
    metfiles_folder = os.path.join(base_path, "metfiles")
    os.makedirs(metfiles_folder, exist_ok=True)
    
    tf = TimezoneFinder()
    dataset = nc.Dataset(netcdf_file, "r")
    mem_driver = gdal.GetDriverByName('MEM')
    
    tif_files = glob.glob(os.path.join(raster_folder, "*.tif"))
    if not tif_files:
        print(f"No TIFF files found in {raster_folder}.")
        dataset.close()
        return

    var_map = {
        "Wind": "WIND",     
        "RH": "RH2",
        "Td": "T2",         # Temperature in Kelvin (to be converted to °C)
        "press": "PSFC",    # Pressure in Pascals (to be converted to kPa)
        "Kdn": "SWDOWN",    
       # "ldown": "GLW"      
    }
    fixed_values = {
        "Q*": -999, "QH": -999, "QE": -999, "Qs": -999, "Qf": -999,
        "snow": -999,"ldown": -999, "fcld": -999, "wuh": -999, "xsmd": -999, "lai_hr": -999,
        "Kdiff": -999, "Kdir": -999, "Wd": -999,
        "rain": 0
    }
    
    time_var = dataset.variables["time"][:]
    time_units = dataset.variables["time"].units
    time_base_date = nc.num2date(time_var, units=time_units, only_use_cftime_datetimes=False)
    
    selected_local_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    
    latitudes = dataset.variables["lat"][:]
    longitudes = dataset.variables["lon"][:]
    min_lon_nc = np.min(longitudes)
    max_lon_nc = np.max(longitudes)
    min_lat_nc = np.min(latitudes)
    max_lat_nc = np.max(latitudes)
    width_nc = len(longitudes)
    height_nc = len(latitudes)
    netcdf_gt = (min_lon_nc, (max_lon_nc - min_lon_nc) / width_nc, 0, max_lat_nc, 0, -(max_lat_nc - min_lat_nc) / height_nc)
    
    columns = [
        'iy', 'id', 'it', 'imin',
        'Q*', 'QH', 'QE', 'Qs', 'Qf',
        'Wind', 'RH', 'Td', 'press',
        'Kdn','rain', 'snow', 'ldown',
        'fcld', 'wuh', 'xsmd', 'lai_hr',
        'Kdiff', 'Kdir', 'Wd'
    ]
    columns_out = [
        "iy", "id", "it", "imin",
        "Q*", "QH", "QE", "Qs", "Qf",
        "Wind", "RH", "Td", "press",
        "rain",
        "Kdn",
        "snow",
        "ldown",
        "fcld",
        "wuh",
        "xsmd",
        "lai_hr",
        "Kdiff",
        "Kdir",
        "Wd"
    ]
    
    for tif_file in tif_files:
        ds_tif = gdal.Open(tif_file)
        if ds_tif is None:
            print(f"Could not open {tif_file}. Skipping.")
            continue
        gt_tif = ds_tif.GetGeoTransform()
        xsize = ds_tif.RasterXSize
        ysize = ds_tif.RasterYSize

        proj_tif = ds_tif.GetProjection()
        srs_tif = osr.SpatialReference()
        srs_tif.ImportFromWkt(proj_tif)
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(srs_tif, target_srs)

        left = gt_tif[0]
        top = gt_tif[3]
        right = left + gt_tif[1] * xsize
        bottom = top + gt_tif[5] * ysize
        corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
        latlon_corners = [transform.TransformPoint(x, y) for x, y in corners]
        lats = [pt[0] for pt in latlon_corners]
        lons = [pt[1] for pt in latlon_corners]

        min_lon_tif, max_lon_tif = min(lons), max(lons)
        min_lat_tif, max_lat_tif = min(lats), max(lats)
        shape = box(min_lon_tif, min_lat_tif, max_lon_tif, max_lat_tif)
        shape_name = os.path.splitext(os.path.basename(tif_file))[0]
        shape_name_clean = re.sub(r'\W+', '_', shape_name).replace("DEM", "metfile", 1)
        output_text_file = os.path.join(metfiles_folder, f"{shape_name_clean}_{selected_date_str}.txt")
        
        lat_center, lon_center = shape.centroid.y, shape.centroid.x
        timezone_name = tf.timezone_at(lng=lon_center, lat=lat_center) or "UTC"
        local_tz = pytz.timezone(timezone_name)
        
        local_start = local_tz.localize(datetime.datetime.combine(selected_local_date, datetime.time(0, 0)))
        local_end = local_tz.localize(datetime.datetime.combine(selected_local_date, datetime.time(23, 59)))
        utc_start = local_start.astimezone(pytz.utc)
        utc_end = local_end.astimezone(pytz.utc)
        
        #print(
        #    f"{shape_name_clean}: Local {selected_date_str} ({timezone_name}) → "
        #    f"UTC {utc_start.date()} {utc_start.hour} to {utc_end.date()} {utc_end.hour}"
        #)
        
        time_indices = [
            idx for idx, dt in enumerate(time_base_date)
            if utc_start <= dt.replace(tzinfo=pytz.utc) <= utc_end
        ]
        if not time_indices:
            print(f"No UTC data found for local date {selected_date_str} in {tif_file}.")
            ds_tif = None
            continue
        print(f"Processing {len(time_indices)} time steps for {shape_name_clean}")
        
        met_new = []
        for t in time_indices:
            utc_time = time_base_date[t].replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(local_tz)
            year = local_time.year
            doy = local_time.timetuple().tm_yday
            hour = local_time.hour
            minute = local_time.minute

            row = [year, doy, hour, minute]
            row.extend([fixed_values[key] for key in ["Q*", "QH", "QE", "Qs", "Qf"]])
            
            for key in ["Wind", "RH", "Td", "press", "Kdn"]:
                var_name = var_map[key]
                if var_name in dataset.variables:
                    try:
                        data_array = dataset.variables[var_name][t, :, :].T
                        rows_arr, cols_arr = data_array.shape

                        # Create an in-memory raster using the netCDF grid
                        data_gt = (min_lon_nc, (max_lon_nc - min_lon_nc) / cols_arr, 0,
                                   max_lat_nc, 0, -(max_lat_nc - min_lat_nc) / rows_arr)
                        data_ds = mem_driver.Create('', cols_arr, rows_arr, 1, gdal.GDT_Float32)
                        data_ds.SetGeoTransform(data_gt)
                        srs = osr.SpatialReference()
                        srs.ImportFromEPSG(4326)
                        data_ds.SetProjection(srs.ExportToWkt())
                        data_ds.GetRasterBand(1).WriteArray(data_array)

                        # Create the mask layer from the shape (polygon from TIFF)
                        mask_ds = mem_driver.Create('', cols_arr, rows_arr, 1, gdal.GDT_Byte)
                        mask_ds.SetGeoTransform(data_gt)
                        mask_ds.SetProjection(srs.ExportToWkt())
                        mask_ds.GetRasterBand(1).Fill(0)

                        ogr_driver = ogr.GetDriverByName('Memory')
                        ogr_ds = ogr_driver.CreateDataSource('temp')
                        layer = ogr_ds.CreateLayer('poly', srs, ogr.wkbPolygon)
                        field_defn = ogr.FieldDefn('id', ogr.OFTInteger)
                        layer.CreateField(field_defn)
                        feature_defn = layer.GetLayerDefn()
                        feature = ogr.Feature(feature_defn)
                        geom = ogr.CreateGeometryFromWkt(shape.wkt)
                        feature.SetGeometry(geom)
                        feature.SetField('id', 1)
                        layer.CreateFeature(feature)
                        gdal.RasterizeLayer(mask_ds, [1], layer, burn_values=[1])
                        mask_array = mask_ds.GetRasterBand(1).ReadAsArray()

                        # Calculate the resolution of the netCDF data_array
                        pixel_width = data_gt[1]
                        pixel_height = abs(data_gt[5])
                        # Calculate the size of the TIFF shape (polygon)
                        shape_width = max_lon_tif - min_lon_tif
                        shape_height = max_lat_tif - min_lat_tif

                        # If the netCDF pixel is larger than the shape, use nearest neighbor
                        if pixel_width > shape_width and pixel_height > shape_height:
                            centroid = shape.centroid
                            col_index = int((centroid.x - min_lon_nc) / pixel_width)
                            row_index = int((max_lat_nc - centroid.y) / pixel_height)
                            # Check for valid indices
                            if 0 <= row_index < rows_arr and 0 <= col_index < cols_arr:
                                mean_value = data_array[row_index, col_index]
                            else:
                                mean_value = -999
                        else:
                            # Otherwise use the masked average as before
                            masked_data = np.where(mask_array == 1, data_array, np.nan)
                            if np.any(~np.isnan(masked_data)):
                                mean_value = np.nanmean(masked_data)
                            else:
                                mean_value = -999

                        # Adjust units if needed
                        if key == "Td" and mean_value != -999:
                            mean_value -= 273.15
                        if key == "press" and mean_value != -999:
                            mean_value /= 1000.0

                        row.append(mean_value)

                        # Clean up temporary datasets
                        data_ds = None
                        mask_ds = None
                        ogr_ds = None
                    except IndexError:
                        print(
                            f"IndexError: Variable {var_name} has incorrect dimensions {dataset.variables[var_name].shape}"
                        )
                        row.append(-999)
                else:
                    row.append(-999)
            
            
            row.append(fixed_values["rain"])
            row.extend([fixed_values[key] for key in ["snow", "ldown", "fcld", "wuh", "xsmd", "lai_hr", "Kdiff", "Kdir", "Wd"]])
            met_new.append(row)

        df = pd.DataFrame(met_new, columns=columns)
        df = df[columns_out]
        with open(output_text_file, "w") as f:
            f.write(" ".join(df.columns) + "\n")
            for _, row in df.iterrows():
                f.write('{:d} {:d} {:d} {:d} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.5f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {:.2f} {: .2f} {: .2f}\n'.format(
                    int(row["iy"]), int(row["id"]), int(row["it"]), int(row["imin"]),
                    row["Q*"], row["QH"], row["QE"], row["Qs"], row["Qf"],
                    row["Wind"], row["RH"], row["Td"], row["press"], row["rain"],
                    row["Kdn"], row["snow"], row["ldown"], row["fcld"], row["wuh"],
                    row["xsmd"], row["lai_hr"], row["Kdiff"], row["Kdir"], row["Wd"]
                ))
        print(f"Metfile saved: {output_text_file}")
        ds_tif = None

    dataset.close()
    print(f"All raster extents processed and metfiles saved in {metfiles_folder}")

# =============================================================================
# Function to process own met file: copies the source met file into new files
# renaming each copy based on the numeric suffix extracted from .tif files.
# =============================================================================
def create_met_files(base_path, source_met_file):
    """
    Copy a given met file to multiple outputs based on the raster tile filenames.

    Parameters:
        base_path (str): Base directory containing "Building_DSM" and where to create "metfiles".
        source_met_file (str): Path to user-provided met file.
    """
    raster_folder = os.path.join(base_path, 'Building_DSM')
    target_folder = os.path.join(base_path, 'metfiles')

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    else:
        shutil.rmtree(target_folder)
        os.makedirs(target_folder)
    
    for file in os.listdir(raster_folder):
        if file.lower().endswith('.tif'):
            name_without_ext = os.path.splitext(file)[0]
            prefix = 'Building_DSM_'
            if name_without_ext.startswith(prefix):
                digits = name_without_ext[len(prefix):]
                new_filename = f'metfile_{digits}.txt'
                target_met_file = os.path.join(target_folder, new_filename)
                shutil.copy(source_met_file, target_met_file)
                print(f"Copied to {target_met_file}")

# =============================================================================
# Main function: checks rasters, creates tiles, and creates metfiles using either a
# user-supplied met file or a netCDF file. Only the parameters required for the chosen
# method need to be provided.
# =============================================================================
def ppr(base_path, building_dsm_filename, dem_filename, trees_filename, landcover_filename,
         tile_size, overlap, selected_date_str, use_own_met,start_time=None, end_time=None, data_source_type=None, data_folder=None,
         own_met_file=None):
    """
    Preprocessing routine to validate raster files, generate tiles, and prepare metfiles for SOLWEIG.

    Parameters:
        base_path (str): Base working directory.
        building_dsm_filename (str): Filename of building DSM raster.
        dem_filename (str): Filename of DEM raster.
        trees_filename (str): Filename of trees raster.
        landcover_filename (str): Filename of landcover raster or None.
        tile_size (int): Tile size in pixels.
        overlap (int): Overlap between tiles in pixels.
        selected_date_str (str): Selected date (YYYY-MM-DD).
        use_own_met (bool): Whether to use a user-provided met file.
        start_time (str): Start datetime (required if not using own met file).
        end_time (str): End datetime (required if not using own met file).
        data_source_type (str): Either 'ERA5' or 'wrfout'.
        data_folder (str): Folder containing input NetCDF files.
        own_met_file (str): Path to user-provided met file (used if use_own_met is True).
    """
    building_dsm_path = os.path.join(base_path, building_dsm_filename)
    dem_path = os.path.join(base_path, dem_filename)
    trees_path = os.path.join(base_path, trees_filename)
    if landcover_filename is not None:
        landcover_path = os.path.join(base_path, landcover_filename)

    # Check that all rasters have matching dimensions, pixel size, and CRS.
    try:
        if landcover_filename is not None:
            check_rasters([building_dsm_path, dem_path, trees_path, landcover_path]) 
        else:
            check_rasters([building_dsm_path, dem_path, trees_path])
            
    except ValueError as error:
        print(error)
        exit(1)

    if landcover_filename is not None:
        rasters = {
            "Building_DSM": building_dsm_path,
            "DEM": dem_path,
            "Trees": trees_path,
            "Landcover": landcover_path
        }
    else: 
        rasters = {
            "Building_DSM": building_dsm_path,
            "DEM": dem_path,
            "Trees": trees_path   
        }  
        
    for tile_type, raster in rasters.items():
        print(f"Creating tiles for {tile_type}...")
        create_tiles(raster, tile_size, overlap, tile_type)
    
    # For metfiles processing, we use the DEM tiles folder.
    dem_tiles_folder = os.path.join(os.path.dirname(dem_path), "DEM")
    
    # Choose between own met file or processed NetCDF file.
    if use_own_met:
        if own_met_file is None:
            print("Error: Please provide the path to your own met file.")
            exit(1)
        create_met_files(base_path, own_met_file)
    else:
        # Ensure all additional required parameters are provided.
        if data_folder is None or data_source_type is None or start_time is None or end_time is None:
            print("Error: When not using your own met file, please provide data_folder, data_source_type, start_time, and end_time.")
            exit(1)
            
        # Define the name (and path) for the processed NetCDF output.
        processed_nc_file = os.path.join(base_path, "Outfile.nc")
        
        if data_source_type.lower() == "era5":
            process_era5_data(start_time, end_time, data_folder, output_file=processed_nc_file)
        elif data_source_type.lower() == "wrfout":
            process_wrfout_data(start_time, end_time, data_folder, output_file=processed_nc_file)
        else:
            print("Error: data_source_type must be either 'ERA5' or 'wrfout'.")
            exit(1)
        
        # Process the generated NetCDF file to create metfiles.
        process_metfiles(processed_nc_file, dem_tiles_folder, base_path, selected_date_str)
