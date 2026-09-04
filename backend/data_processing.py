import pandas as pd

from backend.constants import DATA_DIRECTORY

df = pd.read_csv(DATA_DIRECTORY / "solar.csv")

df = df.astype(object).where(df.notna(), None)