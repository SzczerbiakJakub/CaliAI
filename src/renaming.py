import os
import shutil

def rename_and_move_files(src_dir, dst_dir, prefix="bapl_"):
    # Ensure destination directory exists
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # List all files in the source directory
    files = os.listdir(src_dir)
    
    for index, filename in enumerate(files):
        # Construct full file path
        src_file = os.path.join(src_dir, filename)
        
        # Skip directories
        if os.path.isfile(src_file):
            # Define new filename with prefix and index
            new_filename = f"{prefix}{index}{os.path.splitext(filename)[1]}"
            
            # Construct full destination file path
            dst_file = os.path.join(dst_dir, new_filename)
            
            # Move and rename the file
            shutil.move(src_file, dst_file)

# Example usage
src_directory = "../dataset alpha/ba planche"
dst_directory = "../dataset alpha/bapl"
rename_and_move_files(src_directory, dst_directory)