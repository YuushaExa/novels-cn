import os
import zipfile
import json

# Define input and output directories
NOVEL_DIR = "novel"
OUTPUT_DIR = "output"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def unzip_and_read(zip_path):
    """Unzip a file and read its contents."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all files to a temporary directory
        temp_dir = os.path.splitext(zip_path)[0]
        zip_ref.extractall(temp_dir)
        
        # Read the contents of the extracted files
        contents = {}
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents[file] = f.read()
        
        return contents

def process_novel_folder():
    """Process all zip files in the novel folder."""
    combined_data = {}

    # Iterate over all files in the novel directory
    for file in os.listdir(NOVEL_DIR):
        if file.endswith(".zip"):
            zip_path = os.path.join(NOVEL_DIR, file)
            print(f"Processing {zip_path}...")
            
            # Unzip and read contents
            contents = unzip_and_read(zip_path)
            
            # Add contents to the combined data
            combined_data[file] = contents

    # Save the combined data to a JSON file
    output_json_path = os.path.join(OUTPUT_DIR, "united.json")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
    
    print(f"Combined JSON saved to {output_json_path}")

if __name__ == "__main__":
    process_novel_folder()
