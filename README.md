Title: Radar Precipitation Data toolbox.
Features:
🌦️ Download Radar Data: Seamlessly fetch radar data from public or private sources.
🌍 Geospatial Integration: Compatible with ArcGIS Pro for use in geospatial analysis workflows.
🔄 Customizable: Allows users to specify time ranges and areas of interest.
📊 Processing: Automatically preprocesses radar data into GIS-compatible formats.
📥 Easy Export: Supports exporting data to shapefiles, GeoTIFFs, or other formats for further analysis.

Requirements: 
arcpy: For GIS operations.
requests: For handling API calls and data downloads.
pandas: For data manipulation.
numpy: For numerical processing.

Usage Instructions
1. Installation
Clone the repository:
bash
Copy code
git clone https://github.com/Alijozaghi/RadarDataDownloader.git
Open ArcGIS Pro and add the toolbox (RadarDataDownloader.pyt) to your project.
2. Setup
Make sure ArcGIS Pro has access to Python libraries (e.g., install any missing dependencies via conda).
3. Running the Toolbox
Open the RadarDataDownloader toolbox in ArcGIS Pro.
Fill in the parameters:
Time Range: Specify start and end dates.
Out Put Folder: Save grib files.
Time Interval: Every 2 Minutes of every hour
