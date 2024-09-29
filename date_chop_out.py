import pandas as pd
from pathlib import Path
import os
import re

def extract_domain_name(url):
    match = False
    try:
        pattern = r'https?://(?:www\.)?([^./]+)\.[^/]+'
        match = re.match(pattern, url)
    except:
        if match:
            return match.group(1)
        else:
            return url


def count_words(text):
    """
    Counts the number of words in a given text.

    :param text: String text.
    :return: Integer count of words.
    """
    if pd.isna(text):
        return 0
    # Split the text by whitespace and count the number of elements
    return len(str(text).split())


def filter_csv_by_date(
    input_csv_path,
    output_csv_path,
    date_column,
    cutoff_date='2009-01-01',
    chunksize=100000,
    encoding='utf-8'
):
    """
    Filters rows in a CSV file based on a date column and saves the result to a new CSV file.

    :param input_csv_path: Path to the input CSV file.
    :param output_csv_path: Path to the output CSV file.
    :param date_column: Name of the column containing date information.
    :param cutoff_date: Date string to filter out rows before this date.
    :param chunksize: Number of rows per chunk to process.
    :param encoding: File encoding.
    """
    # Convert cutoff_date string to pandas Timestamp
    # cutoff_timestamp = pd.to_datetime(cutoff_date)

    # Initialize a flag to write headers only once
    write_header = True

    # Create a TextFileReader object for iterating over the input CSV in chunks
    csv_reader = pd.read_csv(
        input_csv_path,
        chunksize=chunksize,
        # parse_dates=[date_column],
        # infer_datetime_format=True,
        encoding=encoding
    )

    for chunk_number, chunk in enumerate(csv_reader, start=1):
        filtered_chunk = chunk[['title', 'selftext','score', 'subreddit', 'num_comments', 'ups']]
        chunk.loc[:, 'created_datetime_utc'] = pd.to_datetime(chunk['created_utc'], unit='s', utc=True)
        filtered_chunk.loc[:, 'Date'] = chunk['created_datetime_utc'].dt.tz_convert('US/Eastern')
        cutoff_timestamp = pd.to_datetime(cutoff_date).tz_localize('US/Eastern')
        # filtered_chunk.loc[:, date_column] = filtered_chunk[date_column].dt.tz_convert('US/Eastern')

        # filtered_chunk.loc[:, 'Url'] = filtered_chunk['Url'].apply(extract_domain_name)
        filtered_chunk = filtered_chunk[(filtered_chunk['title'].apply(count_words) >= 7) |
                                        (filtered_chunk['selftext'].apply(count_words) >= 7)]

        # Filter rows where date_column >= cutoff_date
        filtered_chunk = filtered_chunk[(filtered_chunk[date_column] >= cutoff_timestamp)]

        # If there are any rows after filtering, write them to the output CSV
        if not filtered_chunk.empty:
            filtered_chunk.to_csv(
                output_csv_path,
                mode='w' if write_header else 'a',
                index=False,
                header=write_header,
                encoding=encoding
            )
            print(f"Chunk {chunk_number}: Written {len(filtered_chunk)} records.")
            write_header = False  # Headers are written only once
        else:
            print(f"Chunk {chunk_number}: No records to write.")

def filter_csv_by_date_with_check(
    input_csv_path,
    output_csv_path,
    date_column,
    cutoff_date='2009-01-01',
    chunksize=100000,
    encoding='utf-8',
    overwrite=False
):
    """
    Filters rows in a CSV file based on a date column, checks for existing output file,
    and saves the result to a new CSV file.

    :param input_csv_path: Path to the input CSV file.
    :param output_csv_path: Path to the output CSV file.
    :param date_column: Name of the column containing date information.
    :param cutoff_date: Date string to filter out rows before this date.
    :param chunksize: Number of rows per chunk to process.
    :param encoding: File encoding.
    :param overwrite: If True, overwrite the output file if it exists. Otherwise, skip writing.
    """
    output_path = Path(output_csv_path)

    if output_path.exists():
        if overwrite:
            print(f"Overwriting the existing file: {output_csv_path}")
            output_path.unlink()  # Delete the existing file
        else:
            print(f"The file '{output_csv_path}' already exists. Skipping filtering to avoid overwrite.")
            return  # Exit the function to prevent overwriting

    # Proceed with filtering and saving
    filter_csv_by_date(
        input_csv_path,
        output_csv_path,
        date_column,
        cutoff_date,
        chunksize,
        encoding
    )

# Example Usage
if __name__ == "__main__":
    import sys

    # Example parameters
    INPUT_CSV = 'C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_submissions_merged.csv'          # Path to your input CSV file
    OUTPUT_CSV = 'C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_submissions_merged_chopped.csv'  # Path to the output CSV file
    DATE_COLUMN = 'Date'        # Name of the date column in your CSV
    CUTOFF_DATE = '2009-01-01'       # Date to filter before
    CHUNKSIZE = 100000                # Number of rows per chunk
    OVERWRITE = False                 # Whether to overwrite the output file if it exists

    # df = pd.read_csv('C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_submissions_merged.csv', nrows=100)
    # print(df.head())
    # # print(df['created_utc'])
    # print(df.columns)


    # Check if input file exists
    if not Path(INPUT_CSV).is_file():
        print(f"Input file '{INPUT_CSV}' does not exist. Please provide a valid file path.")
        sys.exit(1)

    # Perform the filtering with file existence check
    filter_csv_by_date_with_check(
        input_csv_path=INPUT_CSV,
        output_csv_path=OUTPUT_CSV,
        date_column=DATE_COLUMN,
        cutoff_date=CUTOFF_DATE,
        chunksize=CHUNKSIZE,
        encoding='utf-8',
        overwrite=OVERWRITE
    )

    print("Filtering completed.")


