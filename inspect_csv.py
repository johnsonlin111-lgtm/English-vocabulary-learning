import requests
import io
import pandas as pd

url = "https://raw.githubusercontent.com/ciwga/Oxford3000_Vocab/master/oxford3000_vocabulary_with_collocations_and_definitions_datasets.csv"
try:
    response = requests.get(url, timeout=10)
    print("CSV Headers:", pd.read_csv(io.StringIO(response.text), nrows=0).columns.tolist())
    print("First row:", pd.read_csv(io.StringIO(response.text), nrows=1).to_dict('records'))
except Exception as e:
    print("Error:", e)
