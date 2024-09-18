import pandas as pd

chunk_size = 50000  # Adjust based on your system's capacity
file_num = 1          # Counter for output files
id_start = 1          # Starting value for 'id' column


# Define the columns you want to keep
columns_to_keep = ['Date', 'Article_title', 'Stock_symbol', 'Article', 'Url']

filename = 'nasdaq'   # Desired filename prefix
for chunk in pd.read_csv('/Users/juhyung/Desktop/data/original/news/nasdaq_exteral_data.csv', chunksize=chunk_size):
    # Filter the columns
    chunk = chunk[columns_to_keep]
    prev_len = len(chunk)
    chunk = chunk.dropna(subset=['Date'], how='any', inplace=False)
    after_len = len(chunk)

    if prev_len != after_len:
        print(f"Dropped {prev_len-after_len} rows")

    # Add 'id' column with unique IDs, formatted with leading zeros
    num_rows = len(chunk)
    id_values = [f"{filename}_{i:09d}" for i in range(id_start, id_start + num_rows)]
    chunk.insert(0, 'id', id_values)

    # Update the starting ID for the next chunk
    id_start += num_rows

    # Format file number with leading zeros
    file_num_padded = f"{file_num:03d}"

    # Save the processed chunk to a new CSV file with formatted file number
    output_file = f'/Users/juhyung/Desktop/data/processed/news/{filename}_external_data_{file_num_padded}.csv'
    chunk.to_csv(output_file, index=False)

    print(f"Completed {filename} {file_num_padded}")
    file_num += 1

chunk_size = 50000  # Adjust based on your system's capacity
file_num = 1          # Counter for output files
id_start = 1          # Starting value for 'id' column

filename = 'all'   # Desired filename prefix
for chunk in pd.read_csv('/Users/juhyung/Desktop/data/original/news/All_external.csv', chunksize=chunk_size):
    # Filter the columns
    chunk = chunk[columns_to_keep]
    prev_len = len(chunk)
    chunk = chunk.dropna(subset=['Date'], how='any', inplace=False)
    after_len = len(chunk)

    if prev_len != after_len:
        print(f"Dropped {prev_len-after_len} rows")

    # Add 'id' column with unique IDs, formatted with leading zeros
    num_rows = len(chunk)
    id_values = [f"{filename}_{i:09d}" for i in range(id_start, id_start + num_rows)]
    chunk.insert(0, 'id', id_values)

    # Update the starting ID for the next chunk
    id_start += num_rows

    # Format file number with leading zeros
    file_num_padded = f"{file_num:03d}"

    # Save the processed chunk to a new CSV file with formatted file number
    output_file = f'/Users/juhyung/Desktop/data/processed/news/{filename}_external_data_{file_num_padded}.csv'
    chunk.to_csv(output_file, index=False)

    print(f"Completed {filename} {file_num_padded}")
    file_num += 1

