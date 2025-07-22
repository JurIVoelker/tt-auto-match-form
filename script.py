import cv2
from exctract_document import find_document_contour, four_point_transform
from preprocess_document import preprocess_document
import os

def extract_document(image_name):
  image_path = f"files/input/{image_name}.jpg"
  image = cv2.imread(image_path)
  document_contour = find_document_contour(image)
  scanned = four_point_transform(image, document_contour)

  preprocessed = preprocess_document(scanned)

  height, width, _ = scanned.shape

  set_results = preprocessed[int(height*0.432):int(height*0.8), int(width*0.615):int(width*0.88)]
  final_results = preprocessed[int(height*0.432):int(height*0.8), int(width*0.87):int(width*0.99)]
  set_results_filename = f"files/output/set_results_{image_name}.jpg"
  final_results_filename = f"files/output/final_results_{image_name}.jpg"
  cv2.imwrite(set_results_filename, set_results)
  cv2.imwrite(final_results_filename, final_results)
  os.remove(image_path)
  return [set_results_filename, final_results_filename]

