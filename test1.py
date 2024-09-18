import pandas as pd

file_name = 'nasdaq_external_data'
file_num = '070'


df = pd.read_csv(f'/Users/juhyung/Desktop/data/processed/news/{file_name}_{file_num}.csv')

print(df)

print(df.columns)

print(len(df))


