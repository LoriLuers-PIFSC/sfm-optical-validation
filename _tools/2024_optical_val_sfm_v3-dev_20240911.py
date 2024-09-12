import fnmatch
from gooey import Gooey, GooeyParser
import csv
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import pandas as pd
from datetime import datetime
import threading
from queue import Queue

# Function to count JPEG files
def fcount(path):
    count = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and not f.startswith('.') and f.lower().endswith('.jpg'):
            count += 1
    return count

def remove_hidden_files(files):
    return [f for f in files if not f.startswith('.')]

def remove_txt_files(files):
    return [f for f in files if not f.endswith('.txt')]

# Function to get the size of a folder
def get_folder_size(pathvalue1):
    total_size = 0
    for dirpath, _, filenames in os.walk(pathvalue1):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    size_in_gb = total_size / (1024 ** 3)  # Convert bytes to GB
    return size_in_gb

# Function to process directories
def process_directory(dir_info):
    src_dir, dir_, exclude_list = dir_info
    current_src = os.path.join(src_dir, dir_)
    current_dir = os.path.basename(current_src)
    parent_dir = os.path.basename(src_dir)
    grandparent_dir = os.path.basename(os.path.dirname(src_dir))

    if any(d in exclude_list for d in [current_dir, parent_dir, grandparent_dir]):
        return None
    print(f"Processing directory: {current_src}")

    file_count = fcount(current_src)
    folder_size = get_folder_size(current_src)

    return (parent_dir, current_dir, file_count, folder_size, current_src)

# Function to generate file count
def generate_file_count(pathvalue1, final_datas, file_qcc_log_filename_path, exclude_list, file_count_header):
    print('--- Imagery file count and size list CSV Started ----')

    dir_info_list = []
    for src_dir, dirs, _ in os.walk(pathvalue1, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_list]
        for dir_ in dirs:
            dir_info_list.append((src_dir, dir_, exclude_list))
    print(f"Processing directory: {src_dir}")
    with ThreadPoolExecutor() as executor:
        future_to_dir = {executor.submit(process_directory, dir_info): dir_info for dir_info in dir_info_list}
        for future in as_completed(future_to_dir):
            result = future.result()
            if result and result[2] > 0:  # Check for non-zero file count
                final_datas.append(result)

    df = pd.DataFrame(final_datas, columns=file_count_header)
    df.to_csv(file_qcc_log_filename_path, index=False)
    print(f'SfM imagery info has been saved to: {file_qcc_log_filename_path}')


    # Export duplicate files to CSV
    #duplicates_csv_path = os.path.join(pathvalue1, '05_duplicate_files.csv')
    #with open(duplicates_csv_path, 'w', newline='') as csvfile:
    #    writer = csv.writer(csvfile)
    #    writer.writerow(['Duplicate File', 'Original File'])
     #   writer.writerows(duplicate_files)
   # print(f'Duplicate files check complete. Results exported to: {duplicates_csv_path}')


#def generate_site_list(site_list_file_info_header, site_list_final_datas, site_list_file_log_filename_path):
 #   print('---- Site list CSV Started ----')
  #  df = pd.DataFrame(site_list_final_datas, columns=site_list_file_info_header)
   # df.to_csv(site_list_file_log_filename_path, index=False)
    #print(f'Site list CSV generated: {site_list_file_log_filename_path}')


# Function to generate site list
def generate_site_list(pathvalue1, exclude_list, output_sitelist_path):
    print('--- Island and site list CSV Started ----')
    islands = []
    sites = []

    # Iterate through the directories in the source directory
    for island in os.listdir(pathvalue1):
        island_path = os.path.join(pathvalue1, island)
        
        # Check if the item is a directory (i.e., an island)
        if os.path.isdir(island_path) and island not in exclude_list:
            print(f"Processing island: {island}")

            # List subdirectories (sites) within this island
            for site in os.listdir(island_path):
                site_path = os.path.join(island_path, site)
                
                if os.path.isdir(site_path) and site not in exclude_list:
                    # Append each island and site pair to the lists
                    islands.append(island)
                    sites.append(site)

    # Create DataFrame and save to CSV
    df = pd.DataFrame({
        'ISLAND': islands,
        'SITE': sites
    })
    df.to_csv(output_sitelist_path, index=False)
    print(f'Island and site information has been saved to: {output_sitelist_path}')

# Function to process island and site

def process_island_site(island, pathvalue1, year_str, queue):
    try:
        island_path = os.path.join(pathvalue1, island)
        
        # Debug statement to verify paths
        print(f"Checking island path: {island_path}")
        
        if os.path.isdir(island_path):
            for site in os.listdir(island_path):
                site_path = os.path.join(island_path, site)
                
                # Debug statement to verify paths
                print(f"Checking site path: {site_path}")
                
                if os.path.isdir(site_path):
                    year_dir_path = os.path.join(site_path, year_str)
                    
                    # Debug statement to verify paths
                    print(f"Checking year path: {year_dir_path}")
                    
                    if os.path.isdir(year_dir_path):
                        # Append each island and site pair to the queue
                        queue.put((island, site))
                        
    except Exception as e:
        print(f"Error processing island {island}: {e}")


# Function to generate fixed site list
def generate_site_list_fixed(pathvalue1, output_sitelist_path_fixed, year=None):
    print('--- Fixed Site: Island and site list CSV for specified year started ----')
    year_str = str(year) if year else None

    islands = []
    sites = []

    try:
        # Iterate through the islands
        for island in os.listdir(pathvalue1):
            island_path = os.path.join(pathvalue1, island)
            if os.path.isdir(island_path):
                # Iterate through the sites
                print(f"Processing island: {island}")

                for site in os.listdir(island_path):
                    site_path = os.path.join(island_path, site)
                    if os.path.isdir(site_path):
                        year_dir_path = os.path.join(site_path, year_str) if year_str else None
                        if not year_str or (os.path.isdir(year_dir_path) if year_str else True):
                            islands.append(island)
                            sites.append(site)

        # Create DataFrame and save to CSV
        if islands and sites:
            df = pd.DataFrame({'ISLAND': islands, 'SITE': sites})
            df.to_csv(output_sitelist_path_fixed, index=False)
            print(f'Island and site information has been saved to: {output_sitelist_path_fixed}')
        else:
            print('No islands or sites found to include in the CSV.')

    except Exception as e:
        print(f"An error occurred: {e}")

# Function to process island year
def process_island_year(island, pathvalue1, year_str, queue):
    try:
        island_path = os.path.join(pathvalue1, island)
        if os.path.isdir(island_path):
            for site in os.listdir(island_path):
                site_path = os.path.join(island_path, site)

                if os.path.isdir(site_path):
                    year_dir_path = os.path.join(site_path, year_str)

                    if os.path.isdir(year_dir_path):
                         # Iterate through folders within the year directory
                        for folder in os.listdir(year_dir_path):
                            folder_path = os.path.join(year_dir_path, folder)
                            
                            if os.path.isdir(folder_path):
                                jpg_count = 0
                                total_size = 0
                                
                                # Iterate through jpg files in the nested folder
                                for root, _, files in os.walk(folder_path):
                                    for file in files:
                                        if file.lower().endswith('.jpg'):
                                            jpg_count += 1
                                            file_path = os.path.join(root, file)
                                            total_size += os.path.getsize(file_path)
                                if jpg_count > 0:
                                    queue.put((island, site, jpg_count, total_size, folder_path))
    except Exception as e:
        print(f"Error processing island {island}: {e}")

# Function to generate fixed file count
def generate_file_count_fixed(pathvalue1, output_file_count_fixed_path, year=None):
    year_str = str(year) if year else None
    print('--- Fixed Site: File count and size for specified year started ----')

    # Use a Queue to safely share data between threads
    queue = Queue()
    
    # List to keep track of threads
    threads = []
    try:
        for island in os.listdir(pathvalue1):
            island_path = os.path.join(pathvalue1, island)
            if os.path.isdir(island_path):
                print(f"Processing island: {island}")
                thread = threading.Thread(target=process_island_year, args=(island, pathvalue1, year_str, queue))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        islands = []
        sites = []
        file_counts = []
        sizes = []
        directories = []
        while not queue.empty():
            island, site, jpg_count, total_size, dir_path = queue.get()
            islands.append(island)
            sites.append(site)
            file_counts.append(jpg_count)
            sizes.append(total_size / (1024 ** 3))  # Convert size to GB
            directories.append(dir_path)

        if islands and sites:
            df = pd.DataFrame({
                'ISLAND': islands,
                'SITE': sites,
                'FILE_COUNT': file_counts,
                'TOTAL_SIZE_GB': sizes,
                'DIRECTORY_PATH': directories
            })
            df.to_csv(output_file_count_fixed_path, index=False)
            print(f'File count and size information has been saved to: {output_file_count_fixed_path}')
        else:
            print('No data found to include in the CSV.')

    except Exception as e:
        print(f"An error occurred: {e}")

# Function to parse command-line arguments
def parse_args():
    parser = GooeyParser(description='App.')
    parser.add_argument('SfM_Folder', widget='DirChooser')
    parser.add_argument('--generate-site-list', action='store_true', help='2. Generate site list CSV file')
    parser.add_argument('--generate-file-count', action='store_true', help='3. Generate imagery count and size CSV file')
    parser.add_argument('--year', type=int, required=True, help='Enter the four-digit year for fixed sites (e.g., 2024)')
    parser.add_argument('--generate-site-list-fixed', action='store_true', help='4. Generate FIXED site list CSV file')
    parser.add_argument('--generate-file-count-fixed', action='store_true', help='5. Generate FIXED imagery count and size CSV file')

    #parser.add_argument('--generate-file-list', action='store_true', help='4. Generate file list CSV file')
    #parser.add_argument('--check-duplicates', action='store_true', help='5. Check for duplicate files')
    #parser.add_argument('--generate-dir-list', action='store_true', help='8. Generate directories list CSV file')

    args = parser.parse_args()
# Validate the year
    if not (2010 <= args.year <= 2030):
        parser.error("Year is out of range and must be a four digit number.")

    return args

#setup GUI
@Gooey(program_name='Development - 2024 SfM Optical Val Tool',
       default_size=(700, 700),   # starting size of the GUI
       menu=[{
        'name': 'SfM Optical Val Tool',
        'items': [{
                'type': 'AboutDialog',
                'menuTitle': 'About',
                'name': 'SfM Optical Val Tool',
                'description': 'Python',
                'version': '1.1',
                'copyright': '2024',
                'website': '',
                'developer': 'Michael Akridge/Lori Luers'}]}])

# Main function
def main():
    # Import user inputs 
    args = parse_args()
    path = args.SfM_Folder
    generate_site_list_flag = args.generate_site_list
    generate_file_count_flag = args.generate_file_count
    year = args.year  # Get the year from user input
    generate_site_list_fixed_flag =args.generate_site_list_fixed
    generate_file_count_flag_fixed = args.generate_file_count_fixed
 # Extract base directory name for filename use
    base_dir_name = os.path.basename(os.path.normpath(path))
    current_datetime = datetime.now().strftime("%m_%d_%Y_%H%M")


    site_list_file_info_header = ['ISLAND', 'SITE']
    output_sitelist_path = os.path.join(path, f'{base_dir_name}_island_site_info_{current_datetime}.csv')
    output_sitelist_path_fixed = os.path.join(path, f'{base_dir_name}_{year}_fixed_site_info_{current_datetime}.csv')

    file_count_header = ['ISLAND', 'SITE', 'FILE_COUNT', 'FOLDER_SIZE_GB', 'DIRECTORY_PATH']
    final_datas = []
    exclude_list = ['MISC', 'SITE', '_SITE', 'Products','_ISLAND', 'ISLAND', 'ISLANDCODE', 'Misc']

    file_qcc_log_filename = base_dir_name + "_SfM_File_count_" + current_datetime + ".csv"
    file_qcc_log_filename_path = os.path.join(path, file_qcc_log_filename)
    output_file_count_fixed_path =  base_dir_name + "_SfM_File_count_" + current_datetime + ".csv"

    if generate_file_count_flag:
        generate_file_count(path, final_datas, file_qcc_log_filename_path, exclude_list,file_count_header)

    if generate_site_list_flag:
        generate_site_list(path, exclude_list, output_sitelist_path)
    
    if generate_site_list_fixed_flag:
        generate_site_list_fixed(path,output_sitelist_path_fixed,year)

    if generate_file_count_flag_fixed:
        generate_file_count_fixed(path, output_sitelist_path_fixed, year)

if __name__ == '__main__':
    main()
