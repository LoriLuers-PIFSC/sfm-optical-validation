# Structure-from-Motion Imagery Validation with File System Tools

## Overview
This tool gathers file system statistics on structure-from-motion imagery. It can pull an island and site list based on location of the imagery (.jpg) as well as pool the number of files an folder size of each site.
These csv files can be used for quality control of directory structure, and also be imported into the Optical App for database validation.

## Prerequisites
- Python

## Installing
1. Download file to local directory
2. Deploy python or Anaconda
3. In command prompt navigate to the directory where it is downloaded

```
python 2024_optical_val_sfm_v3.py
```
4. Select directory of missioncode if random sites, or of region of fixed sites
5. Validate file system stats against database by loading file count info file into the Optical App

## Version Control Platform
- Git

## Resources
- Refer to <a href = "https://github.com/noaa-pifsc/sfm-optical-validation/blob/main/How-to.md">How-To.md</a> for more details on specific functions

## Contact
Developer: Lori Luers
<br>
Email: lori.luers@noaa.gov
<br>
GitHub: LoriLuers-PIFSC

## License
See the [LICENSE.md](./LICENSE.md) for details

## Disclaimer
This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
