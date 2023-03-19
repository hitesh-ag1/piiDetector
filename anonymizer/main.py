from fastapi import FastAPI, File, UploadFile, Response, status
import json
import pandas as pd
from PII_removal_unstructured_text import detectReplacePII
from tqdm import tqdm
import io
from PII_data_processor import find_piis_based_on_column_name
import boto3
import botocore

app = FastAPI()


@app.get("/downloadSampleFiles")
async def download_file(response: Response):
    s3 = boto3.client('s3')
    bucket = 'pii-diagnokare'
    key = "sampleData.zip"

    try:
        fileobj = io.BytesIO()
        s3.download_fileobj(bucket, key, fileobj)
        fileobj.seek(0) 
        response.body = fileobj.getvalue()
        response.headers["Content-Disposition"] = "attachment; filename=sampleData.zip"
        response.headers["Content-Type"] = "application/zip"
        response.status_code = status.HTTP_200_OK
        return response

    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@app.post("/getPIIColumns")
async def getPIIColumns(file: UploadFile = File(...)):
    contents = await file.read()
    return piiColumns(io.BytesIO(contents))

@app.post("/removePIIfromText")
async def removePIIfromText(text: str):
    return detectReplacePII(text)


@app.post("/removePIIfromCol")
async def removePIIfromCol(columnName: str, file: UploadFile = File(...)):
    contents = await file.read()
    return jsonPIIRemover(io.BytesIO(contents), columnName)
    # contents = pd.read_json(io.BytesIO(contents))
    # return {"filename": file.filename, "contents": contents}

def piiColumns(data):
    dataset = pd.read_json(data)
    label_dict = False
    value_label_dict = False
    columns_still_to_check = dataset.columns
    pii_candidates = find_piis_based_on_column_name(dataset, label_dict, value_label_dict, columns_still_to_check, 1)
    return list(pii_candidates.keys())

def jsonPIIRemover(data, fieldName):
    df = pd.read_json(data)
    new_data = []

    for i in tqdm(df[fieldName]):
        new_data.append(detectReplacePII(i))

    col = []
    for i in new_data:
        col.append(i[0])

    # df[fieldName] = col
    df.insert(loc=df.columns.get_loc(fieldName)+1, column="Mod"+fieldName, value=col)
    df = df.to_dict(orient='records')
    return df