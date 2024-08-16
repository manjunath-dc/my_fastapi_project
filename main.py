from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.exc import SQLAlchemyError
from db import get_db, engine, metadata
from utils import parse_csv, add_technology_column
import os
import tempfile

app = FastAPI()

@app.post("E:/my_fastAPI_project/companies.csv")
async def upload_csv(file: UploadFile = File(...), db=Depends(get_db)):
    try:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name
            tmp.write(file.file.read())
        
        # Parse and process the CSV file
        df = parse_csv(file_path)
        df = add_technology_column(df)

        # Extract the column names and types
        columns = []
        for col in df.columns:
            if col == "Technology Company":
                columns.append(Column(col, BOOLEAN))
            else:
                columns.append(Column(col, String))

        # Creating a new table
        table = Table("companies", metadata, *columns, extend_existing=True)
        metadata.create_all(bind=engine)

        return {"message": "Table created successfully", "columns": df.columns.tolist()}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    finally:
        # To Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
