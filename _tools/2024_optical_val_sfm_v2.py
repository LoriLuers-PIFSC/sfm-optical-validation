import fnmatch
from gooey import Gooey, GooeyParser
import csv
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import pandas as pd
from datetime import datetime
#Ctrl + / to comment code
#tab to move right
#shift tab to move left


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


def get_folder_size(pathvalue1):
    total_size = 0
    for dirpath, _, filenames in os.walk(pathvalue1):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    # Convert size from bytes to gigabytes
    size_in_gb = total_size / (1024 ** 3)  # 1 GB = 1024^3 bytes
    return size_in_gb

def process_directory(dir_info):
    src_dir, dir_, exclude_list = dir_info
    current_src = os.path.join(src_dir, dir_)
    current_dir = os.path.basename(current_src)
    parent_dir = os.path.basename(src_dir)
    grandparent_dir = os.path.basename(os.path.dirname(src_dir))

    if any(d in exclude_list for d in [current_dir, parent_dir, grandparent_dir]):
        return None

    file_count = fcount(current_src)
    folder_size = get_folder_size(current_src)

    return (parent_dir, current_dir, file_count, folder_size, current_src)

def generate_file_count(pathvalue1, final_datas, file_qcc_log_filename_path, exclude_list,file_count_header):
    print('--- Imagery file count and size list CSV Started ----')

    # Collect all directories to process
    dir_info_list = []
    for src_dir, dirs, _ in os.walk(pathvalue1, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_list]  # Exclude specified directories
        for dir_ in dirs:
            dir_info_list.append((src_dir, dir_, exclude_list))

    # Process directories in parallel
    with ThreadPoolExecutor() as executor:
        future_to_dir = {executor.submit(process_directory, dir_info): dir_info for dir_info in dir_info_list}
        for future in as_completed(future_to_dir):
            result = future.result()
            if result:
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


def generate_site_list(pathvalue1, exclude_list, output_sitelist_path):
    print('--- Island and site list CSV Started ----')
    islands = []
    sites = []

    # Iterate through the directories in the source directory
    for island in os.listdir(pathvalue1):
        island_path = os.path.join(pathvalue1, island)
        
        # Check if the item is a directory (i.e., an island)
        if os.path.isdir(island_path) and island not in exclude_list:
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

# def generate_dir_list(pathvalue1, dir_list_file_path):
#     print('---- Generate directories list started ----')
#     all_directories = []
#     for src_dir, dirs, _ in os.walk(pathvalue1, topdown=True):
#         for dir_ in dirs:
#             full_dir_path = os.path.join(src_dir, dir_)
#             all_directories.append(full_dir_path)
    
#     # Write all directories to CSV
#     with open(dir_list_file_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Directory'])
#         writer.writerows([[dir_] for dir_ in all_directories])
#     print(f'Directories list CSV generated: {dir_list_file_path}')    

    
# def load_exclude_list(exclude_list_file_path):
#     exclude_list = []
#     with open(exclude_list_file_path, 'r') as f:
#         csv_reader = csv.reader(f)
#         next(csv_reader)  # Skip header
#         for row in csv_reader:
#             exclude_list.append(row[0])
#     return exclude_list



# def generate_dir_list(pathvalue1, dir_list_file_path):
#     print('---- Generate directories list started ----')
#     all_directories = []
#     for src_dir, dirs, _ in os.walk(pathvalue1, topdown=True):
#         for dir_ in dirs:
#             full_dir_path = os.path.join(src_dir, dir_)
#             all_directories.append(full_dir_path)
    
#     # Write all directories to CSV
#     with open(dir_list_file_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Directory'])
#         writer.writerows([[dir_] for dir_ in all_directories])
#     print(f'Directories list CSV generated: {dir_list_file_path}')    

    
# def load_exclude_list(exclude_list_file_path):
#     exclude_list = []
#     with open(exclude_list_file_path, 'r') as f:
#         csv_reader = csv.reader(f)
#         next(csv_reader)  # Skip header
#         for row in csv_reader:
#             exclude_list.append(row[0])
#     return exclude_list
#define user inputs
def parse_args():
    parser = GooeyParser(description='App.')
    parser.add_argument('SfM_Folder', widget='DirChooser')
    parser.add_argument('--generate-site-list', action='store_true', help='2. Generate site list CSV file')
    parser.add_argument('--generate-file-count', action='store_true', help='3. Generate imagery count and size CSV file')
    #parser.add_argument('--generate-file-list', action='store_true', help='4. Generate file list CSV file')
    #parser.add_argument('--check-duplicates', action='store_true', help='5. Check for duplicate files')
    #parser.add_argument('--generate-dir-list', action='store_true', help='8. Generate directories list CSV file')
    return parser.parse_args()
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
                'version': '1.0',
                'copyright': '2024',
                'website': '',
                'developer': 'Lori Luers'}]}])

#Main functions
def main():
    # Import user inputs 
    args = parse_args()
    path = args.SfM_Folder
    generate_site_list_flag = args.generate_site_list
    generate_file_count_flag = args.generate_file_count
 # Extract base directory name for filename use
    base_dir_name = os.path.basename(os.path.normpath(path))
    current_datetime = datetime.now().strftime("%m_%d_%Y_%H%M")


    site_list_file_info_header = ['ISLAND', 'SITE']
    output_sitelist_path = os.path.join(path, f'{base_dir_name}_island_site_info_{current_datetime}.csv')

    file_count_header = ['ISLAND', 'SITE', 'FILE_COUNT', 'FOLDER_SIZE_GB', 'DIRECTORY_PATH']
    final_datas = []
    exclude_list = ['MISC', 'SITE', '_SITE', 'Products', 'ISLAND', 'ISLANDCODE']

    file_qcc_log_filename = base_dir_name + "_SfM_File_count_" + current_datetime + ".csv"
    file_qcc_log_filename_path = os.path.join(path, file_qcc_log_filename)

    if generate_file_count_flag:
        generate_file_count(path, final_datas, file_qcc_log_filename_path, exclude_list,file_count_header)

    if generate_site_list_flag:
        generate_site_list(path, exclude_list, output_sitelist_path)

if __name__ == '__main__':
    main()
