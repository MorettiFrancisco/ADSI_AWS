import boto3
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/load-bucket-file")
async def load_bucket(name: str, file: UploadFile = File(...)):
    s3 = boto3.client("s3")
    bucket = "adsi-bucket"
    s3.upload_fileobj(file.file, bucket, file.filename)
    file_url = f"https://{bucket}.s3.amazonaws.com/{file.filename}"
    return {"message": f"Loaded file {file.filename}. file url: {file_url}"}


@app.delete("/delete-bucket-file")
async def delete_bucket_file(name: str):
    s3 = boto3.client("s3")
    bucket = "adsi-bucket"
    response = s3.delete_object(Bucket=bucket, Key=name)
    return {"message": f"{response}"}

@app.post("/load-dynamo")
async def load_dynamo(dni_alumno: str, nombre_parcial: str, nota_parcial: float):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ADSI_Prueba")
    table.put_item(Item={"dni_alumno": dni_alumno, "nombre_parcial": nombre_parcial, "nota_parcial": nota_parcial})
    return {"message": f"Loaded parcial {dni_alumno} in table {table.name}"} 

@app.get("/get-dynamo")
async def get_dynamo(dni_alumno: str):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ADSI_Prueba")
    response = table.get_item(Key={"dni_alumno": dni_alumno})
    item = response.get("Item")
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
