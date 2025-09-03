"""
Central configuration for file paths and app constants.
"""
from pathlib import Path

# Data files (prefer accurate coordinates if present)
DATA_FILE_ACCURATE = Path("nl_highschools_accurate_coordinates.csv")
DATA_FILE_FALLBACK_WITH_COORDS = Path("nl_highschools_with_coordinates.csv")
DATA_FILE_RAW = Path("nl_highschools_full.csv")

# Client storage
CLIENT_FILE = Path("client_schools.json")

# Map defaults
NL_CENTER = (52.1326, 5.2913)  # Geographic center of the Netherlands
DEFAULT_ZOOM = 7

# Columns used in the dataset
ID_COL = "vestigings_id"
LAT_COL = "latitude"
LON_COL = "longitude"
NAME_COL = "school_name"
CITY_COL = "city"
PROVINCE_COL = "province"
WEBSITE_COL = "website"
PHONE_COL = "phone_formatted"
LEVELS_COL = "levels_offered"

# Derived column names
IS_CLIENT_COL = "is_client"

# Education levels
RELEVANT_LEVELS = ["VMBO", "HAVO", "VWO"]
IRRELEVANT_LEVELS = ["PRO", "BRUGJAAR", "MAVO"]



# GitHub persistence defaults (used if a token is provided via env or Streamlit secrets)
GITHUB_OWNER = "pieterfranken"
GITHUB_REPO = "nl-highschools-dashboard"
GITHUB_BRANCH = "main"
GITHUB_CLIENTS_PATH = "client_schools.json"
