from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import uuid

app = FastAPI()

# Serve static files from the "files" directory
app.mount("/files", StaticFiles(directory="files"), name="files")

@app.post("/api/results")
async def read_root(file: Annotated[bytes, File()]):
  from script import extract_document
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
    
  return {
    "set_results": file_names[0],
    "final_results": file_names[1]
  }
  # set_results_url = "https://s3.voelkerlabs.de/data/set_results.jpg"
  # final_results_url = "https://s3.voelkerlabs.de/data/final_results.jpg"

  # results = get_results(set_results_url, final_results_url)
  # return results