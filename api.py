from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import uuid
import os
from ai import get_results
from script import extract_document


app = FastAPI()

# Serve static files from the "files" directory
app.mount("/files", StaticFiles(directory="files"), name="files")

@app.get("/health")
def health_check():
  return {"status": "healthy"}

@app.post("/api/results")
async def read_root(file: Annotated[bytes, File()]):
  # from ai import get_results

  filename = uuid.uuid4().hex
  filepath = f"files/input/{filename}.jpg"

  with open(filepath, "wb") as f:
    f.write(file)
  
  file_names = []
  try:
    file_names = extract_document(filename)
    print(file_names)
  except:
    return {"error": "Failed to process the document"}, 400
  
  image_prefix = "https://tt-auto-match-form.voelkerlabs.de/" if os.environ.get("API_URL") is None else os.environ.get("API_URL")
  set_results = image_prefix + file_names[0]
  final_results = image_prefix + file_names[1]

  results = get_results(set_results, final_results)
  # os.remove(file_names[0])  
  # os.remove(file_names[1])  

  return results
