import cv2
import numpy as np

def find_document_contour(image):
    # Reduziere die Bildgröße für bessere Konturerkennung
    scale_percent = 50  # Reduziere die Größe auf 50% der Originalgröße
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # Konturen finden
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    # Suche nach einem 4-Ecken-Kontur (vermutlich das Blatt Papier)
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            # Skaliere die Punkte zurück auf die Originalgröße
            return (approx.reshape(4, 2) * (100 / scale_percent)).astype(int)
    
    raise Exception("Kein Dokument erkannt.")

def order_points(pts):
    # Ordne Punkte: oben-links, oben-rechts, unten-rechts, unten-links
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]      # oben-links
    rect[2] = pts[np.argmax(s)]      # unten-rechts
    rect[1] = pts[np.argmin(diff)]   # oben-rechts
    rect[3] = pts[np.argmax(diff)]   # unten-links
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # Zielgrößen berechnen
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Zielpunkte
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # Perspektiv-Transformation
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

# 📷 Bild laden

