import os
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from docx import Document
from docx.shared import Pt

# --- Configuration ---
INPUT_DIR = Path("novel")
OUTPUT_DIR = Path("output")
# Use max workers available, but you can cap it, e.g., max_workers=4
MAX_WORKERS = os.cpu_count()

def convert_txt_to_docx(txt_path: Path) -> str:
    """
    Converts a single TXT file to a DOCX file.

    Args:
        txt_path: The path to the input TXT file.

    Returns:
        A string message indicating the result of the conversion.
    """
    try:
        # Create DOCX document
        doc = Document()
        # You can also set default font here if needed
        # style = doc.styles['Normal']
        # font = style.font
        # font.name = 'Arial'
        # font.size = Pt(11)

        # Read TXT file line-by-line for memory efficiency
        with txt_path.open('r', encoding='utf-8') as f:
            for line in f:
                paragraph_text = line.strip()
                if paragraph_text:  # Skip empty lines
                    p = doc.add_paragraph(paragraph_text)
                    p.paragraph_format.space_after = Pt(6)

        # Save DOCX file
        output_filename = f"{txt_path.stem}.docx"
        output_path = OUTPUT_DIR / output_filename
        doc.save(output_path)
        return f"Successfully converted {txt_path.name} to {output_filename}"

    except Exception as e:
        return f"Error converting {txt_path.name}: {e}"


def main():
    """
    Main function to find and convert all TXT files in parallel.
    """
    start_time = time.time()

    if not INPUT_DIR.exists():
        print(f"Error: Input directory '{INPUT_DIR}' does not exist.")
        return

    # Ensure the output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Find all .txt files, case-insensitively
    txt_files = list(INPUT_DIR.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(txt_files)} TXT file(s). Starting conversion with up to {MAX_WORKERS} parallel processes...")

    success_count = 0
    failure_count = 0

    # Use a process pool to convert files in parallel
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Create a future for each file conversion
        future_to_file = {executor.submit(convert_txt_to_docx, txt_file): txt_file for txt_file in txt_files}

        for future in as_completed(future_to_file):
            result_message = future.result()
            print(result_message)
            if "Successfully" in result_message:
                success_count += 1
            else:
                failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    print("\n--- Conversion Summary ---")
    print(f"Successfully converted: {success_count}")
    print(f"Failed to convert:     {failure_count}")
    print(f"Total files processed: {len(txt_files)}")
    print(f"Total time taken:      {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
