
from fastapi import FastAPI, Request, UploadFile, Response
from fastapi.responses import HTMLResponse,JSONResponse,FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
from config.db import conn
from bson import Binary

templates = Jinja2Templates(directory="templates")

app = FastAPI()

notes_collection = conn.note.notes

from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def index():
    return {'message':"Hello User"}

@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(request: Request,file: UploadFile):
    try:
        dest = Path("uploads") / file.filename
        dest.parent.mkdir(parents=True, exist_ok=True)

        form = await request.form()
        form_data = dict(form)

        title = form_data.get("name")

        file_object = await file.read()

        with open(f"{dest}","wb")as f:
            f.write(file_object)

        await file.close()
        print("Uploaded successfully to folder!")

        notes_collection.insert_one({
            "title": title,
            "image": file.filename
        })

        print("Data saved to MongoDB successfully!")
        return {"file_uploading": True}

    except Exception as e:
        return {'file_uploading': False}
    

@app.get("/image/{image_name}")
async def render_image(image_name: str, response: Response):
    file_path = f"uploads/{image_name}"

    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"message": "Image not found!"}
    
@app.get("/allnotes")
async def get_notes(request:Request):
    all_docs = []
    docs = notes_collection.find({})
    for doc in docs:
        print("Document from database:", doc)  # Debugging print to inspect document structure
        try:
            all_docs.append({
                "id": str(doc['_id']),  # Convert ObjectId to string if necessary
                "title": doc["title"],
                "image": doc['image'],
            })
        except TypeError as e:
            print(f"Error processing document: {doc} - {e}")  # Debugging for unexpected structure
            continue  # Skip documents that do not match expected structure
    print("The all_docs details are: ",all_docs)

    return templates.TemplateResponse(request=request,name="index.html", context={"newDocs":all_docs})
    # return templates.TemplateResponse("image.html", {"request": request, "all_docs": all_docs})
    