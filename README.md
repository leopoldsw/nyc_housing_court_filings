# nyc_housing_court_filings
Landlord and tenant cases in NYC housing courts from the New York State Office of Court Administration (OCA).

## Description

This dataset contains all landloard and tenant cases related to properties located in New York City filed on or after January 1, 2019.

Only certain variables are selected:

- Randomly generated case identifier (indexnumberid)
- Case Filing Date (filedate)
- Property Type (propertytype): residential or commercial
- Case Type (classification): non-payment, harassment etc.
- Zipcode of the property (zip)


## Data Files

- **nyc_hcf.csv**: Complete dataset containing all NYC housing court filings with available data (no date restriction)
- **nyc_hcf_from_2019.csv**: Filtered dataset containing only NYC housing court filings from January 1, 2019 onwards

Both files contain landlord-tenant cases filtered to NYC zip codes with the variables listed above.

## Source Source

Raw data files are created by the Housing Data Coalition (HDC). URL is https://github.com/austensen/oca.


## Useful Links

NYC Housing Court: https://www.nycourts.gov/courts/nyc/housing/ 

