import os
import zipfile
import json
from pathlib import Path

def process_novels():
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    combined_data = []
    
    # Process each ZIP file in the novel directory
    novel_dir = Path("novel")
    for zip_file in novel_dir.glob("*.zip"):
        try:
            # Create a temporary directory for extraction
            temp_dir = Path(f"temp_{zip_file.stem}")
            temp_dir.mkdir(exist_ok=True)
            
            # Extract the ZIP file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Process each chapter file in the extracted directory
            for chapter_file in temp_dir.glob("*"):
                if chapter_file.is_file():
                    # Use chapter filename as title (without extension)
                    title = chapter_file.stem
                    
                    # Read chapter content
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Add to combined data
                    combined_data.append({
                        "title": title,
                        "content": content
                    })
            
            # Clean up temporary directory
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()
            
        except Exception as e:
            print(f"Error processing {zip_file}: {str(e)}")
    
    # Save combined data to JSON (overwrite if exists)
    combined_path = output_dir / "combined.json"
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(combined_data)} chapters into {combined_path}")

if __name__ == "__main__":
    process_novels()
