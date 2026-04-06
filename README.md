# NYC Housing Court Filings

Landlord and tenant cases in NYC housing courts from the New York State Office of Court Administration (OCA).

## Description

This dataset contains all landlord and tenant cases related to properties located in New York City. Two versions are provided:

- A **complete dataset** with all available filings (no date restriction)
- A **filtered dataset** with filings from January 1, 2019 onwards

Only certain variables are selected:

- **indexnumberid**: Randomly generated case identifier
- **fileddate**: Case filing date
- **propertytype**: Residential or commercial
- **classification**: Case type (non-payment, holdover, harassment, etc.)
- **zip**: 5-digit zip code of the property


## Getting Started

### 1. Open the project in VS Code

Open VS Code, then go to **File > Open Folder** and select the `nyc_housing_court_filings` folder.

### 2. Open the terminal

In VS Code, open the built-in terminal:
- **Mac**: Press `` Ctrl + ` `` (control + backtick)
- **Windows**: Press `` Ctrl + ` `` (control + backtick)
- Or go to **Terminal > New Terminal** in the menu bar

### 3. Set up a virtual environment

This keeps the project's packages separate from your other Python projects.

**Mac / Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your terminal line.

### 4. Install dependencies

```
pip install -r requirements.txt
```

### 5. Run the script

```
python main.py
```

The script downloads approximately 700 MB of data from the OCA database. This may take **several minutes** depending on your internet speed. You will see progress updates as it runs.


## What the Script Does

1. Downloads raw case index and address data from the OCA public S3 bucket
2. Extracts 5-digit zip codes from address records
3. Filters to cases in NYC using a zip code reference file
4. Saves two versions of the dataset (complete + post-2019), each as CSV and compressed .gz


## Output Files

After running the script, you will find these files in `data/uploads/`:

| File | Description |
|------|-------------|
| `nyc_hcf.csv` | Complete dataset, all available years |
| `nyc_hcf.csv.gz` | Compressed version of the complete dataset |
| `nyc_hcf_from_2019.csv` | Filtered to filings from January 1, 2019 onwards |
| `nyc_hcf_from_2019.csv.gz` | Compressed version of the 2019+ dataset |


## Reference Data

The file `references/nyc_zpnb_crosswalk.csv` maps NYC zip codes to neighborhoods and boroughs. It is used by the script to filter cases to NYC only. Columns:

- **Zip**: 5-digit zip code
- **PUMA**: Public Use Microdata Area code
- **Neighborhood**: Neighborhood name
- **Borough**: Manhattan, Brooklyn, Queens, Bronx, or Staten Island


## Source

Raw data files are created by the Housing Data Coalition (HDC): https://github.com/austensen/oca


## Useful Links

- NYC Housing Court: https://www.nycourts.gov/courts/nyc/housing/
