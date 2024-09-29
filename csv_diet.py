import pandas as pd
from tqdm import tqdm


def skip_and_save_rows_pandas(input_file, output_file, initial_skip, skip_between_saves):
    chunks = pd.read_csv(input_file,
                         skiprows=range(1, initial_skip + 1),
                         chunksize=skip_between_saves)
    header = True
    for chunk in chunks:
        if header == True:
            chunk.iloc[[0]].to_csv(output_file, mode='w', header=True, index=False)
            header = False
        else:
            chunk.iloc[[0]].to_csv(output_file, mode='a', header=False, index=False)


if __name__ == "__main__":
    input_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/news/news_merged_chopped.csv"
    output_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/news/news_merged_chopped_diet.csv"
    initial_skip = 840000
    skip_between_saves = 600

    skip_and_save_rows_pandas(input_csv, output_csv, initial_skip, skip_between_saves)

    input_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_comments_merged_chopped.csv"
    output_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_comments_merged_chopped_diet.csv"
    initial_skip = 0
    skip_between_saves = 300

    skip_and_save_rows_pandas(input_csv, output_csv, initial_skip, skip_between_saves)

    input_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_submissions_merged_chopped.csv"
    output_csv = r"C:/Users/Ju Hyung Kang/Desktop/merged/reddit/reddit_submissions_merged_chopped_diet.csv"
    initial_skip = 0
    skip_between_saves = 60

    skip_and_save_rows_pandas(input_csv, output_csv, initial_skip, skip_between_saves)
