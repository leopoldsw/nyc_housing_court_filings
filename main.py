import pandas as pd
import urllib.request
import urllib.error
import tempfile
import sys
import os
from pathlib import Path

# All paths relative to this script's location (works from any working directory)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "uploads"
REFERENCES_DIR = BASE_DIR / "references"

S3_BASE_URL = "https://oca-2-dev.s3.amazonaws.com/public"
OCA_INDEX_URL = f"{S3_BASE_URL}/oca_index.csv"
OCA_ADDRESSES_URL = f"{S3_BASE_URL}/oca_addresses.csv"


def download_file(url, description):
    """Download a file from a URL to a temporary file, showing progress."""

    def progress_hook(block_count, block_size, total_size):
        downloaded = block_count * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 // total_size)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            print(f"\r       Downloading {description}... {percent}% ({downloaded_mb:.0f} / {total_mb:.0f} MB)", end="", flush=True)
        else:
            downloaded_mb = downloaded / (1024 * 1024)
            print(f"\r       Downloading {description}... {downloaded_mb:.0f} MB", end="", flush=True)

    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_path = tmp_file.name
        tmp_file.close()
        urllib.request.urlretrieve(url, tmp_path, reporthook=progress_hook)
        print()  # newline after progress
        return tmp_path
    except (urllib.error.URLError, urllib.error.HTTPError, ConnectionError, OSError) as e:
        print()
        print(f"\n  Error: Could not download {description}.")
        print(f"  URL: {url}")
        print(f"  Details: {e}")
        print("\n  Please check your internet connection and try again.")
        print("  If the problem persists, the data source may be temporarily unavailable.")
        sys.exit(1)


def load_nyc_zips():
    """Load the list of valid NYC zip codes from the crosswalk reference file."""
    crosswalk_path = REFERENCES_DIR / "nyc_zpnb_crosswalk.csv"
    try:
        crosswalk = pd.read_csv(crosswalk_path)
        return list(crosswalk["Zip"])
    except FileNotFoundError:
        print(f"\n  Error: Reference file not found: {crosswalk_path}")
        print("  This file is required to filter cases to NYC zip codes.")
        print("  Please make sure the 'references' folder is intact.")
        sys.exit(1)


def process_addresses(oca_addresses):
    """Clean zip codes and deduplicate address records."""
    total_rows = len(oca_addresses)

    # Extract 5-digit zip from full postal code
    oca_addresses["zip"] = oca_addresses["postalcode"].str[:5]
    oca_addresses = oca_addresses.drop(columns="postalcode")

    # Safe conversion: coerce non-numeric zips to NaN, then drop them
    oca_addresses["zip"] = pd.to_numeric(oca_addresses["zip"], errors="coerce")
    invalid_zips = oca_addresses["zip"].isna().sum()
    oca_addresses = oca_addresses.dropna(subset=["zip"])
    oca_addresses["zip"] = oca_addresses["zip"].astype(int)

    # Keep one address per case (deduplicate before merging)
    before_dedup = len(oca_addresses)
    oca_addresses = oca_addresses.drop_duplicates(subset=["indexnumberid"])
    after_dedup = len(oca_addresses)

    print(f"       {total_rows:,} address records loaded")
    if invalid_zips > 0:
        print(f"       {invalid_zips:,} records with invalid zip codes removed")
    print(f"       {after_dedup:,} unique cases after deduplication")

    return oca_addresses


def build_datasets(oca_index, oca_addresses, nyc_zips):
    """Merge index with addresses, filter to NYC, split into complete and 2019+ datasets."""
    # Single merge
    df = oca_index.merge(oca_addresses, on="indexnumberid", how="left")
    total_before_filter = len(df)

    # Filter to NYC zip codes
    df = df[df["zip"].isin(nyc_zips)].sort_values("fileddate")
    total_after_filter = len(df)
    dropped = total_before_filter - total_after_filter

    # Split by date
    df_complete = df
    df_2019 = df[df["fileddate"] >= "2019-01-01"]

    print(f"       {total_before_filter:,} total cases after merge")
    print(f"       {dropped:,} cases outside NYC zip codes removed")
    print(f"       {len(df_complete):,} cases in complete dataset")
    print(f"       {len(df_2019):,} cases in post-2019 dataset")

    return df_complete, df_2019


def save_datasets(df_complete, df_2019):
    """Save datasets as both CSV and compressed .gz files."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files_to_save = [
        (df_2019, "nyc_hcf_from_2019.csv"),
        (df_complete, "nyc_hcf.csv"),
    ]

    try:
        for df, filename in files_to_save:
            csv_path = DATA_DIR / filename
            gz_path = DATA_DIR / f"{filename}.gz"

            df.to_csv(csv_path, index=False)
            df.to_csv(gz_path, index=False, compression="gzip")

            csv_size_mb = csv_path.stat().st_size / (1024 * 1024)
            gz_size_mb = gz_path.stat().st_size / (1024 * 1024)
            print(f"       {filename} ({csv_size_mb:.1f} MB)")
            print(f"       {filename}.gz ({gz_size_mb:.1f} MB)")
    except OSError as e:
        print(f"\n  Error: Could not save output files: {e}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("NYC Housing Court Filings - Data Update")
    print("=" * 60)
    print()

    # Step 1: Load NYC zip codes
    print("[1/5] Loading NYC zip codes...")
    nyc_zips = load_nyc_zips()
    print(f"       {len(nyc_zips)} NYC zip codes loaded")
    print()

    # Step 2: Download case index
    print("[2/5] Downloading case index (this may take several minutes)...")
    index_tmp = download_file(OCA_INDEX_URL, "case index")
    oca_index = pd.read_csv(
        index_tmp,
        parse_dates=["fileddate"],
        usecols=["indexnumberid", "fileddate", "propertytype", "classification"],
    )
    os.unlink(index_tmp)
    print(f"       {len(oca_index):,} cases loaded")
    print()

    # Step 3: Download addresses
    print("[3/5] Downloading address data (this may take several minutes)...")
    addr_tmp = download_file(OCA_ADDRESSES_URL, "addresses")
    oca_addresses = pd.read_csv(
        addr_tmp,
        usecols=["indexnumberid", "postalcode"],
    )
    os.unlink(addr_tmp)
    print()

    # Step 4: Process and merge
    print("[4/5] Processing data...")
    oca_addresses = process_addresses(oca_addresses)
    df_complete, df_2019 = build_datasets(oca_index, oca_addresses, nyc_zips)
    print()

    # Step 5: Save
    print("[5/5] Saving output files...")
    save_datasets(df_complete, df_2019)
    print()

    print("=" * 60)
    print("Done! Output files are in:", DATA_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
