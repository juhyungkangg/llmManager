import pandas as pd
import csv
import sys

# Increase the field size limit to handle large fields in the CSV file
# csv.field_size_limit(sys.maxsize)

# Define file path and chunk size
file_path = 'C:/Users/Ju Hyung Kang/Desktop/news_merged_chopped.csv'
chunk_size = 50000  # Number of rows per chunk

# Set the number of lines to skip
skip_lines = 3651000

# File paths for the output files
output_file_after_2020 = 'C:/Users/Ju Hyung Kang/Desktop/data_after_2020.csv'
output_file_before_2020 = 'C:/Users/Ju Hyung Kang/Desktop/data_before_2020.csv'

# Read the header first to preserve column names
header = pd.read_csv(file_path, nrows=0).columns

# Initialize output files by writing the header
with open(output_file_after_2020, 'w', newline='', encoding='utf-8') as f_after, \
     open(output_file_before_2020, 'w', newline='', encoding='utf-8') as f_before:
    # Write headers to both files
    pd.DataFrame(columns=header).to_csv(f_after, index=False)
    pd.DataFrame(columns=header).to_csv(f_before, index=False)

# Flags to track if it's the first write (headers already written)
# Since headers are already written above, we can set these flags to True
header_written_after_2020 = True
header_written_before_2020 = True

# Read and process the CSV file in chunks, skipping the specified number of lines
for chunk in pd.read_csv(
    file_path,
    chunksize=chunk_size,
    skiprows=range(1, skip_lines + 1),
    names=header,
    header=0,
    low_memory=False
):
    # Drop rows where 'Date' could not be parsed
    chunk.dropna(subset=['Date', 'Article'], inplace=True)

    # Split the chunk into two dataframes based on the date condition
    data_after_2020 = chunk[chunk['Date'] >= '2020-01-01']
    data_before_2020 = chunk[chunk['Date'] < '2020-01-01']

    # Append the data to their respective CSV files
    if not data_after_2020.empty:
        data_after_2020.to_csv(
            output_file_after_2020,
            mode='a',  # Append mode
            header=False,  # Header already written
            index=False
        )

    if not data_before_2020.empty:
        data_before_2020.to_csv(
            output_file_before_2020,
            mode='a',  # Append mode
            header=False,  # Header already written
            index=False
        )
print("CSV processing completed successfully.")
