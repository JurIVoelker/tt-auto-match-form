import cv2
from exctract_document import find_document_contour, four_point_transform
from preprocess_document import preprocess_document
import easyocr

image = cv2.imread("files/input/image.jpg")
document_contour = find_document_contour(image)
scanned = four_point_transform(image, document_contour)

preprocessed = preprocess_document(scanned)

height, width, _ = scanned.shape

def remove_black_borders(image):
  _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

  inv = 255 - binary

  hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
  remove_horizontal = cv2.morphologyEx(inv, cv2.MORPH_OPEN, hor_kernel, iterations=1)

  ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
  remove_vertical = cv2.morphologyEx(inv, cv2.MORPH_OPEN, ver_kernel, iterations=1)

  table_lines = cv2.add(remove_horizontal, remove_vertical)

  cleaned = cv2.subtract(inv, table_lines)

  result = 255 - cleaned
  return result



result_region = preprocessed[int(height*0.432):int(height*0.8), int(width*0.615):int(width*0.99)]
cv2.imwrite("files/output/region_of_interest.jpg", result_region)

remove_black_borders_result = remove_black_borders(result_region)
cv2.imwrite("files/output/cleaned_region.jpg", remove_black_borders_result)

height, width = remove_black_borders_result.shape

first_row = remove_black_borders_result[0:int(height*0.08), 0:remove_black_borders_result.shape[1]]
cv2.imwrite("files/output/first_row.jpg", first_row)

reader = easyocr.Reader(['de'])
results = reader.readtext("files/output/first_row.jpg")
for (bbox, text, confidence) in results:
    print(f'Text: {text} (Konfidenz: {confidence:.2f})')

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:'
# text = pytesseract.image_to_string("files/output/first_row.jpg", config=custom_config)
# print(text)


cv2.imwrite("files/output/scanned.jpg", preprocessed)





