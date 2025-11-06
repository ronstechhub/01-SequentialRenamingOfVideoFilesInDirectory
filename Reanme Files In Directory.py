import os

def rename_files_sequentially(directory_path):
    """
    Renames all files in the given directory sequentially (e.g., part 1.txt, part 2.jpg).

    Args:
        directory_path (str): The path to the directory containing the files.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Processing files in: {directory_path}")

    try:
        # Get a list of all files in the directory
        # We use os.listdir to get all entries, then filter for files
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        files.sort() # Sort files to ensure consistent renaming order

        if not files:
            print("No files found in the directory to rename.")
            return

        # Iterate through the files and rename them
        for index, filename in enumerate(files):
            # Construct the full old file path
            old_file_path = os.path.join(directory_path, filename)

            # Get the file extension (e.g., .txt, .jpg)
            # os.path.splitext splits the path into (root, ext)
            file_name_without_ext, file_extension = os.path.splitext(filename)

            # Create the new file name
            new_filename = f"part {index + 1}{file_extension}"
            new_file_path = os.path.join(directory_path, new_filename)

            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

        print("\nFile renaming completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- Main execution ---
if __name__ == "__main__":
    # Prompt the user for the directory path
    input_directory = input("Enter the path to the directory containing the files: ")

    # Call the function to rename the files
    rename_files_sequentially(input_directory)