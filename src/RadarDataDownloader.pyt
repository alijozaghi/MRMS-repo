# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 00:04:15 2024

@author: alijo
"""

import arcpy
import os
import requests
import datetime
import gzip
import shutil
import numpy as np
import xarray as xr
import pyproj
from rasterio.transform import from_origin
from rasterio.crs import CRS
import geopandas as gpd

class Toolbox(object):
    """This class will contain the tools for this toolbox."""

    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Radar Data Downloader"
        self.alias = "AJ"
        self.tools = [RadarDataDownloader]  # Add your tools here

class RadarDataDownloader(object):
    """This tool will add a field to an input feature class."""

    def __init__(self):
        """Define the tool (tool name and label)."""
        self.label = "Radar Data Downloader"
        self.alias = "Radar Rainfall"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions for the tool."""
        params = [
            arcpy.Parameter(
                displayName="Output Folder",
                name="output_folder",
                datatype="DEFolder",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Start Date (YYYY-MM-DD HH:MM)",
                name="start_date",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="End Date (YYYY-MM-DD HH:MM)",
                name="end_date",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Interval (BIMINUTELY or HOURLY)",
                name="interval",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
            )
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def execute(self, parameters, messages):
        """Execute the tool."""
        output_folder = parameters[0].valueAsText
        start_date = datetime.datetime.strptime(parameters[1].valueAsText, "%Y-%m-%d %H:%M")
        end_date = datetime.datetime.strptime(parameters[2].valueAsText, "%Y-%m-%d %H:%M")
        interval = parameters[3].valueAsText

        Syr = start_date.year
        Smon = start_date.month
        Sdy = start_date.day
        Shr = start_date.hour
        Smin = start_date.minute

        Eyr = end_date.year
        Emon = end_date.month
        Edy = end_date.day
        Ehr = end_date.hour
        Emin = end_date.minute

        if interval == 'BIMINUTELY':
            self.get_RadarOnly_QPE_01H(output_folder, Syr, Smon, Sdy, Shr, Smin, Eyr, Emon, Edy, Ehr, Emin)
        elif interval == 'HOURLY':
            self.get_RadarOnly_QPE_24H(output_folder, Syr, Smon, Sdy, Shr, Eyr, Emon, Edy, Ehr)

    def unzip_gz_file(self, input_gz_path, output_path):
        with gzip.open(input_gz_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def get_RadarOnly_QPE_01H(self, pathMRMS, Syr, Smon, Sdy, Shr, Smin, Eyr, Emon, Edy, Ehr, Emin):
        Ssec = 0
        Esec = 0
        start_date = datetime.datetime(Syr, Smon, Sdy, Shr, Smin, Ssec)
        end_date = datetime.datetime(Eyr, Emon, Edy, Ehr, Emin, Esec)
        delta = datetime.timedelta(minutes=2)

        while start_date < end_date:
            year = str(start_date.year).zfill(4)
            mn = str(start_date.month).zfill(2)
            dy = str(start_date.day).zfill(2)
            hr = str(start_date.hour).zfill(2)
            mint = str(start_date.minute).zfill(2)
            sec = str(start_date.second).zfill(2)
            URL = f'https://mtarchive.geol.iastate.edu/{year}/{mn}/{dy}/mrms/ncep/RadarOnly_QPE_01H/RadarOnly_QPE_01H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2.gz'
            folder_path = os.path.join(pathMRMS, 'RadarOnly_QPE_01H')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            FILENAME = os.path.join(folder_path, f'RadarOnly_QPE_01H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2.gz')
            result = requests.get(URL)
            try:
                result.raise_for_status()
                with open(FILENAME, 'wb') as f:
                    f.write(result.content)
            except:
                print(f'requests.get() returned an error code {result.status_code}')
            output_path = os.path.join(folder_path, f'RadarOnly_QPE_01H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2')
            self.unzip_gz_file(FILENAME, output_path)
            try:
                os.remove(FILENAME)
            except PermissionError:
                print(f"PermissionError: Unable to delete {FILENAME}. The file might be in use.")
            start_date += delta
        print('DONE!')

    def get_RadarOnly_QPE_24H(self, pathMRMS, Syr, Smon, Sdy, Shr, Eyr, Emon, Edy, Ehr):
        Smin = 0
        Ssec = 0
        Emin = 0
        Esec = 0
        start_date = datetime.datetime(Syr, Smon, Sdy, Shr, Smin, Ssec)
        end_date = datetime.datetime(Eyr, Emon, Edy, Ehr, Emin, Esec)
        delta = datetime.timedelta(minutes=60)

        while start_date < end_date:
            year = str(start_date.year).zfill(4)
            mn = str(start_date.month).zfill(2)
            dy = str(start_date.day).zfill(2)
            hr = str(start_date.hour).zfill(2)
            mint = str(start_date.minute).zfill(2)
            sec = str(start_date.second).zfill(2)
            URL = f'https://mtarchive.geol.iastate.edu/{year}/{mn}/{dy}/mrms/ncep/RadarOnly_QPE_24H/RadarOnly_QPE_24H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2.gz'
            folder_path = os.path.join(pathMRMS, 'RadarOnly_QPE_24H')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            FILENAME = os.path.join(folder_path, f'RadarOnly_QPE_24H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2.gz')
            result = requests.get(URL)
            try:
                result.raise_for_status()
                with open(FILENAME, 'wb') as f:
                    f.write(result.content)
            except:
                print(f'requests.get() returned an error code {result.status_code}')
            output_path = os.path.join(folder_path, f'RadarOnly_QPE_24H_00.00_{year}{mn}{dy}-{hr}{mint}{sec}.grib2')
            self.unzip_gz_file(FILENAME, output_path)
            try:
                os.remove(FILENAME)
            except PermissionError:
                print(f"PermissionError: Unable to delete {FILENAME}. The file might be in use.")
            start_date += delta
        print('DONE!')
