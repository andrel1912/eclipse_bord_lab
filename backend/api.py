from fastapi import FastAPI
from backend.data_processing import df

app = FastAPI()


@app.get("/")
def home():
    return {"message": "eClipseBord API is running"}


@app.get("/data")
def get_data():
    return df.to_dict(orient="records")