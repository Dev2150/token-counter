import os
import re
import csv
from collections import Counter
import sys
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox # Optional: for error messages

def is_number(s):
    """Checks if a string is a number (integer or float, positive or negative)."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def count_keywords(file_path, output_csv_path, encoding='utf-8'):
    """
    Counts unique keywords in a file and exports to CSV.

    Args:
        file_path (str): The path to the input file.
        output_csv_path (str): The path for the output CSV file.
        encoding (str): The character encoding of the input file (default: 'utf-8').
                        Try 'windows-1252' if 'utf-8' fails.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    print(f"Analyzing file: {file_path}")

    keyword_counts = Counter()
    total_size = os.path.getsize(file_path)
    bytes_read = 0
    last_percent = -1

    # Regex to find quoted strings (to ignore them)
    quoted_string_pattern = re.compile(r'"[^"]*"')

    # Regex to find potential keywords (sequences of word characters)
    # We'll filter these further
    word_pattern = re.compile(r'\w+')

    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            for line in f:
                # Update progress
                # Estimate bytes read by adding the length of the line (encoded)
                # This is an approximation but works reasonably well for progress
                bytes_read += len(line.encode(encoding, errors='ignore'))
                current_percent = int((bytes_read / total_size) * 100)

                if current_percent > last_percent:
                    print(f"Reading: {current_percent}%", end='\r', file=sys.stdout)
                    last_percent = current_percent

                # --- Keyword Extraction Logic ---

                # 1. Remove comments (anything after #)
                line = line.split('#', 1)[0]

                # 2. Remove quoted strings (they are values, not keywords)
                line = quoted_string_pattern.sub(' ', line)

                # 3. Replace structural operators with spaces to separate tokens
                line = line.replace('=', ' ').replace('{', ' ').replace('}', ' ')

                # 4. Split the line into potential tokens by whitespace
                tokens = line.split()

                # 5. Process tokens
                for token in tokens:
                    # Ignore empty tokens
                    if not token:
                        continue

                    # Ignore tokens that are just operators (should be handled by replace, but safety)
                    if token in ['=', '{', '}']:
                         continue

                    # Ignore numbers
                    if is_number(token):
                        continue

                    # If it's not a number, not a string (already removed), and not an operator,
                    # consider it a potential keyword.
                    # We could add more checks here if needed (e.g., specific symbols)
                    # but \w+ check below is a good start.

                    # Use regex to find actual "words" within the token
                    # This handles cases like "keyword:" or "keyword," if they weren't fully separated
                    # However, given the replacement of operators, simple split is often enough.
                    # Let's stick to the simple split tokens and filter.

                    # Basic check: does it look like a word?
                    # This helps filter out stray symbols that might remain
                    if word_pattern.fullmatch(token):
                         keyword_counts[token] += 1


        # Ensure 100% is printed at the end
        print("Reading: 100%", file=sys.stdout)
        print("\nFile reading complete.")

    except FileNotFoundError:
        # This was already checked, but good practice
        print(f"\nError: File not found at '{file_path}'")
        return
    except Exception as e:
        print(f"\nAn error occurred while reading the file: {e}")
        print(f"Try changing the 'encoding' parameter. Common alternatives are 'windows-1252'.")
        return

    # Prepare data for CSV
    # Sort by count descending, then keyword alphabetically ascending
    sorted_keywords = sorted(keyword_counts.items(), key=lambda item: (-item[1], item[0]))

    # Write to CSV
    print(f"Writing results to {output_csv_path}")
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Keyword", "Count"]) # Header row
            csv_writer.writerows(sorted_keywords)

        print("CSV file created successfully.")

    except IOError as e:
        print(f"Error writing CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing CSV: {e}")


if __name__ == "__main__":
    print("Clausewitz Keyword Counter")
    print("--------------------------")

    # Create a hidden root window for tkinter dialogs
    root = tk.Tk()
    root.withdraw() # Hide the main window

    # --- Ask for Input File ---
    input_file = fd.askopenfilename(
        title="Select File to Analyze",
        initialdir=".", # Start in the current directory
        filetypes=[
            ("Clausewitz Files", "*.gui *.txt *.yml *.gfx *.log *.asset *.shader *.sfx *.settings"), # Common extensions
            ("All files", "*.*")
        ]
    )

    # Check if the user cancelled the dialog
    if not input_file:
        print("File selection cancelled. Exiting.")
        sys.exit() # Exit the script

    # # --- Ask for Output CSV File ---
    # output_file = fd.asksaveasfilename(
    #     title="Save Keyword Counts CSV As...",
    #     initialdir=".", # Start in the current directory
    #     defaultextension=".csv", # Automatically add .csv if not typed
    #     filetypes=[
    #         ("CSV files", "*.csv"),
    #         ("All files", "*.*")
    #     ]
    # )

    # # Check if the user cancelled the dialog
    # if not output_file:
    #     print("Save location selection cancelled. Exiting.")
    #     sys.exit() # Exit the script

    # --- Run the counting process ---
    # You can add a try/except here for the main function call if needed

    # --- Automatically Determine Output CSV Path ---
    # Get the workspace root directory (one level up from src)
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + f'\\exports\\'
    
    # Create exports directory if it doesn't exist
    os.makedirs(script_dir, exist_ok=True)

    # Get the base name of the input file (e.g., "frontend.gui")
    input_filename_only = os.path.basename(input_file)

    # Create the output filename by adding ".csv"
    output_filename = input_filename_only + ".csv"

    # Combine the script directory and the output filename
    output_file = os.path.join(script_dir, output_filename)

    print(f"Output will be saved to: {output_file}")

    count_keywords(input_file, output_file, encoding='utf-8')
