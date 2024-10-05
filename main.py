import boto3
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
import asyncpg

app = FastAPI()
pgsql_conn = None
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



# Crear la conexión al iniciar la aplicación
@app.on_event("startup")
async def startup():
    global pgsql_conn
    pgsql_conn = await asyncpg.connect(
        database="database-1",
        user="postgres",
        password="trabajointegrador",
        host="database-1.c52oa2aa4of2.us-west-2.rds.amazonaws.com",
        port="5432",
    )


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

@app.post("/load-rds")
async def load_rds(name: str, surname: str):
    try:
        await pgsql_conn.execute("INSERT INTO alumnos (nombre, apellido) VALUES ($1, $2)", name, surname)
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}