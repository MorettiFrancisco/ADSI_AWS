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


@app.post("/load-bucket")
async def load_bucket(name: str, file: UploadFile = File(...)):
    s3 = boto3.client("s3")
    bucket = "BUCKET_NAME"
    s3.upload_fileobj(file.file, bucket, file.filename)
    file_url = f"https://{bucket}.s3.amazonaws.com/{file.filename}"
    return {"message": f"Loaded file {file.filename}. file url: {file_url}"}


@app.post("/load-dynamo")
async def load_dynamo(name: str, description: str, price: float):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("TABLE_NAME")
    table.put_item(Item={"name": name, "description": description, "price": price})
    return {"message": f"Loaded item {name} in table {table.name}"}


@app.get("/get-dynamo")
async def get_dynamo():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("TABLE_NAME")
    response = table.scan()
    return response["Items"]

@app.put("/update-dynamo")
async def update_dynamo(name: str, price: float):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("TABLE_NAME")
    table.update_item(
        Key={"name": name},
        UpdateExpression="set price = :p",
        ExpressionAttributeValues={":p": price},
    )
    return {"message": f"Updated price of item {name} in table {table.name}"}

@app.delete("/delete-dynamo")
async def delete_dynamo(name: str):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("TABLE_NAME")
    table.delete_item(Key={"name": name})
    return {"message": f"Deleted item {name} in table {table.name}"}