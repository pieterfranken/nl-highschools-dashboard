# Dutch High Schools Dataset Builder

This project creates a comprehensive dataset of all Dutch high schools (VO - Voortgezet Onderwijs) by merging official DUO (Dienst Uitvoering Onderwijs) datasets.

## What the script does

The `build_nl_highschools_dataset.py` script:

1. **Merges two official DUO datasets:**
   - School addresses and basic information (`adressen_vo.csv`)
   - Student enrollment data per school location (`leerlingen_vo_per_vestiging.csv`)

2. **Processes and standardizes the data:**
   - Normalizes column names and handles different CSV formats
   - Creates unique school identifiers (BRIN + vestigingsnummer)
   - Identifies education levels offered (VMBO, HAVO, VWO, PRO, Gymnasium)
   - Calculates total enrollment per school

3. **Optional enrichments:**
   - TTO (Tweetalig Onderwijs) schools from `tto_scholen.csv`
   - IB (International Baccalaureate) schools from `ib_scholen.csv`

4. **Outputs a comprehensive CSV file** (`nl_highschools_full.csv`) with:
   - **School identification**: BRIN codes, vestigingsnummer, names
   - **Contact information**: Formatted phone numbers, websites, digital presence flags
   - **Address details**: Street, postcode, city, province, municipality
   - **Education structure**: Detailed breakdown of offered levels (PRO, VMBO, MAVO, HAVO, VWO, BRUGJAAR)
   - **Geographic classifications**: Multiple regional systems (COROP, RMC, vacation regions)
   - **School metrics**: Size categories, enrollment statistics, students per grade
   - **Administrative details**: Board information, denomination, governance structure
   - **Languages of instruction**: Dutch, TTO, IB programs

## Required Data Files

### Download from DUO (duo.nl)

You need to download these two CSV files from the DUO website and place them in the same folder as the script:

1. **`adressen_vo.csv`** - "Alle vestigingen VO"
   - Contains addresses and basic information for all VO school locations
   - Available at: [DUO Onderwijsdata](https://duo.nl/open_onderwijsdata/voortgezet-onderwijs/adressen/)

2. **`leerlingen_vo_per_vestiging.csv`** - "VO-leerlingen per vestiging naar onderwijstype"
   - Contains student enrollment data per school location by education type
   - Available at: [DUO Onderwijsdata](https://duo.nl/open_onderwijsdata/voortgezet-onderwijs/leerlingen-vo/)

### Optional Enhancement Files

These files are optional but will enrich the dataset if available:

3. **`tto_scholen.csv`** (optional)
   - List of schools offering TTO (Tweetalig Onderwijs - Bilingual Education)
   - Should contain columns: `school_name`, `city`

4. **`ib_scholen.csv`** (optional)
   - List of schools offering IB (International Baccalaureate)
   - Should contain columns: `school_name`, `city`

## Setup and Installation

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   # For data processing only:
   pip install pandas

   # For interactive dashboard:
   pip install pandas streamlit plotly folium streamlit-folium
   ```

3. **Download the required CSV files** from DUO and place them in this folder

## Usage

### 1. Build the Dataset
Run the data processing script:
```bash
python build_nl_highschools_dataset.py
```

### 2. Launch Interactive Dashboard
Start the web-based interactive dashboard:
```bash
python run_dashboard.py
```

Or directly with Streamlit:
```bash
streamlit run app.py
```

The dashboard will open in your web browser at `http://localhost:8501`


### 2b. New Multipage App Structure

This repo now uses a modular structure and Streamlit multipage app:

- lib/
  - config.py — central constants and paths
  - data.py — load/save schools and clients, resolve CSVs
  - maps.py — Folium map builder with client highlighting
- pages/
  - 1_🗺️_Map.py — interactive map of schools (clients in green)
  - 2_🎯_Clients.py — manage client schools (mark/unmark)
- app.py — Overview page with KPIs and finder

Run the app:

```bash
streamlit run app.py
```

Tips:
- Use the Map page to see geocoded schools (clients highlighted).
- Use the Clients page to mark a school as an Examify client; this writes client_schools.json.
- If coordinates are missing, run one of the geocoding scripts (e.g., geocode_all_schools.py) to populate latitude/longitude.

### 3. Deploy to Streamlit Cloud (Optional)
Deploy your dashboard for public access:

1. **Create a GitHub repository** and upload your project files
2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub
3. **Create new app** pointing to your repository and `app.py`
4. **Your dashboard will be live** at `https://your-app-name.streamlit.app`

📋 **See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions**

## Expected Output

The script will create `nl_highschools_full.csv` containing **34 columns**:

### Basic Information
- **vestigings_id**: Unique identifier (BRIN + vestigingsnummer)
- **brin**: School's BRIN number
- **vestigingsnummer**: Location number within the school
- **school_name**: Name of the school location

### Address & Contact
- **street**, **house_no**, **house_add**: Address components
- **postcode**, **city**: Postal code and city
- **province**: Dutch province
- **municipality**, **municipality_code**: Municipality details
- **phone_formatted**: Formatted Dutch phone number
- **website**: School website URL
- **has_website**: Boolean flag for digital presence

### Administrative
- **board**, **board_code**: School board information
- **denomination**: Religious/philosophical orientation (Openbaar, Bijzonder, etc.)

### Geographic Classifications
- **corop**: COROP region
- **rmc_regio**: RMC region
- **onderwijsgebied**: Education area
- **vacation_region**: Dutch vacation region (Noord/Midden/Zuid)

### Education Structure
- **education_structure**: Raw education structure from DUO
- **levels_offered**: Formatted list of education levels
- **PRO**, **VMBO**, **MAVO**, **HAVO**, **VWO**, **BRUGJAAR**: Boolean flags for each level
- **languages**: Languages of instruction (Dutch, English TTO/IB)

### Enrollment & Metrics
- **enrollment_total**: Total number of students
- **school_size_category**: Small/Medium/Large/Very Large classification
- **students_per_grade**: Average students per grade level

## Data Sources

- **DUO (Dienst Uitvoering Onderwijs)**: Official Dutch education data
- **TTO/IB data**: Optional supplementary sources for bilingual education programs

## 🚀 Interactive Dashboard Features

The included Streamlit dashboard (`app.py`) provides:

### 📊 **Overview Dashboard**
- Real-time metrics and KPIs
- Province and school size distributions
- Education structure analysis
- Interactive filtering by province, education level, size, and denomination

### 🗺️ **Geographic Analysis**
- Schools by vacation region with enrollment statistics
- Top cities by school count
- Regional digital presence analysis

### 🎓 **Education Level Analysis**
- Detailed breakdown of education levels offered
- Comprehensive schools analysis (schools offering 4+ levels)
- Visual charts and statistics

### 📞 **Contact Information**
- Digital presence analysis by province
- Contact availability statistics
- Phone and website coverage metrics

### 🔍 **School Finder**
- Search functionality by school name or city
- Detailed school information display
- Clickable website links and formatted contact details

### 🎛️ **Interactive Features**
- **Dynamic Filtering**: Filter by province, education levels, school size, denomination
- **Real-time Updates**: All charts and metrics update based on selected filters
- **Responsive Design**: Works on desktop and mobile devices
- **Export Capabilities**: Download filtered data and charts

## Notes

- The script automatically detects the latest school year in the enrollment data
- Column names are normalized to handle variations in DUO file formats
- Missing data is handled gracefully with fallback options
- Schools without enrollment data will still appear in the output with empty enrollment fields
- The interactive dashboard requires additional dependencies (streamlit, plotly, folium)


### Streamlit Cloud persistence of clients (optional)

To persist client_schools.json when running on Streamlit Cloud, add a GitHub token with repo scope:

- In Streamlit Cloud app settings, add a secret `GITHUB_TOKEN: <your_token>`
- The app will read from/write to `client_schools.json` in the repo on branch `main`
- Locally, it still writes to client_schools.json on disk
