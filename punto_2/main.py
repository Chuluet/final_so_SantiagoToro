import io
import csv
import boto3
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
s3_client = boto3.client("s3")
BUCKET_NAME = "final-so-stm"


class Item(BaseModel):
    name: str
    edad: int
    altura: float


@app.post("/insert")
def insert_item(item: Item):
    try:
        filename = "data.csv"

        try:
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
            content = response["Body"].read().decode("utf-8")
            existing_df = pd.read_csv(io.StringIO(content))
        except s3_client.exceptions.NoSuchKey:
            existing_df = pd.DataFrame(columns=["name", "edad", "altura"])

        new_data = pd.DataFrame([{
            "name": item.name,
            "edad": item.edad,
            "altura": item.altura
        }])

        updated_df = pd.concat([existing_df, new_data], ignore_index=True)

        csv_buffer = io.StringIO()
        updated_df.to_csv(csv_buffer, index=False)

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=csv_buffer.getvalue(),
            ContentType="text/csv"
        )

        return {
            "message": f"Registro agregado exitosamente a '{filename}'.",
            "total_filas": len(updated_df)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rows")
def get_row_count():
    
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        if "Contents" not in response or len(response["Contents"]) == 0:
            raise HTTPException(status_code=404, detail="No hay archivos en S3.")

        filename = response["Contents"][0]["Key"]

        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        content = obj["Body"].read().decode("utf-8")

        df = pd.read_csv(io.StringIO(content))
        row_count = len(df)

        return {"filename": filename, "row_count": row_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
