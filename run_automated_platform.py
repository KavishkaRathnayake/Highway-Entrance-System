import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
import numpy as np
from server import manage_numberplate_db
import cvzone
from datetime import datetime  # Import for date and time

# Initialize PaddleOCR
ocr = PaddleOCR()

# Initialize video capture and YOLO model
cap = cv2.VideoCapture('tc.mp4')
model = YOLO("best_float32.tflite")
with open("coco1.txt", "r") as f:
    class_names = f.read().splitlines()

# Function to perform OCR on an image array
def perform_ocr(image_array):
    if image_array is None:
        raise ValueError("Image is None")

    # Perform OCR on the image array
    results = ocr.ocr(image_array, rec=True)  # rec=True enables text recognition
    detected_text = []

    # Process OCR results
    if results and results[0]:
        for result in results[0]:
            text = result[1][0]
            detected_text.append(text)

    # Join all detected texts into a single string
    return ''.join(detected_text)

# Mouse callback function to print mouse position
def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

# Predefined region and counters
area = [(5, 180), (3, 249), (984, 237), (950, 168)]
counter = []
detected_plates = {}  # Dictionary to store detected plates and track IDs

# Frame skipping (process every 3rd frame)
frame_skip = 3
frame_count = 0

# Function to generate and print ticket
def print_ticket(plate_text):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket = f"Ticket for Plate: {plate_text}\nDate and Time: {current_time}\n"
    
    print(ticket)  # Print ticket to console
    
    # Optionally save the ticket to a text file
    with open("tickets.txt", "a") as file:
        file.write(ticket + "\n")  # Append ticket to the file

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip processing for this frame

    frame = cv2.resize(frame, (800, 400))  # Reduce resolution for faster processing
    results = model.track(frame, persist=True, imgsz=256)

    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.int().cpu().tolist()
        class_ids = results[0].boxes.cls.int().cpu().tolist()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        confidences = results[0].boxes.conf.cpu().tolist()

        for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
            c = class_names[class_id]
            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            result = cv2.pointPolygonTest(np.array(area, np.int32), (cx, cy), False)
            if result >= 0:
                if track_id not in counter:
                    counter.append(track_id)

                    # Crop and process the image for OCR only if not detected before
                    crop = frame[y1:y2, x1:x2]
                    crop = cv2.resize(crop, (120, 70))

                    if track_id not in detected_plates:
                        # Perform OCR only for new plates
                        text = perform_ocr(crop)
                        text = text.replace('(', '').replace(')', '').replace(',', '').replace(']', '').replace('-', ' ')

                        if text:  # If OCR successfully detects something
                            detected_plates[track_id] = text  # Save the plate in dictionary
                            manage_numberplate_db(text)  # Update database
                            print(f"Detected Plate: {text}")

                            # Print ticket for the detected plate
                            print_ticket(text)  # Generate and print a ticket

    # Display count of unique detected plates
    mycounter = len(detected_plates)
    cvzone.putTextRect(frame, f'Plates: {mycounter}', (50, 60), 1, 1)
    cv2.polylines(frame, [np.array(area, np.int32)], True, (255, 0, 0), 2)
    cv2.imshow("RGB", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
