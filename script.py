import cv2
from exctract_document import find_document_contour, four_point_transform
from preprocess_document import preprocess_document
import os
from minio import Minio

minio = Minio(
    os.environ.get("MINIO_ENDPOINT", "s3.ttc.voelkerlabs.de"),
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=True
)

def extract_document(image_name):
  image_path = f"files/input/{image_name}.jpg"
  if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file {image_path} does not exist.")

  image = cv2.imread(image_path)
  document_contour = find_document_contour(image)
  scanned = four_point_transform(image, document_contour)

  preprocessed = preprocess_document(scanned)

  height, width, _ = scanned.shape

  set_results = preprocessed[int(height*0.432):int(height*0.8), int(width*0.615):int(width*0.88)]
  final_results = preprocessed[int(height*0.432):int(height*0.8), int(width*0.87):int(width*0.99)]
  set_results_filename = f"set_results_{image_name}.jpg"
  set_results_filepath = f"files/output/{set_results_filename}"
  final_results_filename = f"final_results_{image_name}.jpg"
  final_results_filepath = f"files/output/{final_results_filename}"

  cv2.imwrite(set_results_filepath, set_results)
  cv2.imwrite(final_results_filepath, final_results)
  minio.fput_object("tt-auto-match-form", set_results_filename, set_results_filepath)
  minio.fput_object("tt-auto-match-form", final_results_filename, final_results_filepath)
  os.remove(set_results_filepath)
  os.remove(final_results_filepath)
  os.remove(image_path)
  return [set_results_filename, final_results_filename]

if __name__ == "__main__":
    image_name = "image"
    extract_document(image_name)