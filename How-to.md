## Background
- Our shift to collecting imagery for data collection prompts developing tools to optimize quality control of our imagery and integration with the database.
- This tool assists in file system QC, when used in conjunction with the Optical App will query outliers for sites missing imagery, imagery missing sites, and other issues. 

## File Directory Structure
- StRS (Random sites): CRUISE > ISLAND > SITE > IMAGERY (.jpg)
- Fixed Sites: REGION > ISLAND > SITE > YEAR > YYYYMMDD_SITE_CRUISE_REGIONCODE > IMAGERY (.jpg)

## Generating a site list
- Pulls from the directory structure, so enter in the parent directory to the list of islands.
- e.g. using the structure above for Random sites, use 'CRUISE' and for Fixed Sites use 'REGION' directory)
- For fixed sites, a year must be input since within each island there are multiple years.
- For now, year does need to be input for StRS sites but will not affect the function
- Should take no more than a few minutes (typically quite fast, within 30 seconds)

## Generating file counts
- This function searches for .jpg files, and uses the directory structure from there to provide site and island information
- Can be done island-level / other directory levels since it just searches for jpegs 
- Requires a year for fixed sites.
- Excludes folders without images, ‘MISC’, and ‘Products’
- Using virtual machine at PIFSC : ~500 GB in ~6 minutes for 9 fixed sites
- Can also be used to save diver time entering number of images and folder size into the database
- Validation with the Database
- Load into the Optical App ‘Optical Validation Module’ to see what imagery has yet to be sorted, or imagery that exists but is not flagged in the database for SfM activity.

