from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import torch

app = Flask(__name__)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize variables to store the top-left and bottom-right points of the rectangle
drawing = False
crosswalk_start = (0, 0)
crosswalk_end = (0, 0)

# Mouse callback function to draw the rectangle
def draw_rectangle(event, x, y, flags, param):
    global crosswalk_start, crosswalk_end, drawing

    # Start drawing when left mouse button is pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        crosswalk_start = (x, y)

    # Update the rectangle coordinates as the mouse is dragged
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            crosswalk_end = (x, y)

    # Finish drawing when left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        crosswalk_end = (x, y)

# Route to render the HTML form for video upload
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle video file upload
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video_file' not in request.files:
        return 'No file part'

    file = request.files['video_file']
    if file.filename == '':
        return 'No selected file'

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('process_video', filename=file.filename))

# Route to process the uploaded video (crosswalk detection)
@app.route('/process/<filename>')
def process_video(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Video capture and processing code (same as your current detection logic)
    cap = cv2.VideoCapture(video_path)

    # Create a window and bind the mouse callback function to it
    cv2.namedWindow('Crosswalk Detection')
    cv2.setMouseCallback('Crosswalk Detection', draw_rectangle)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Draw the selected crosswalk area (rectangle)
        if crosswalk_start != (0, 0) and crosswalk_end != (0, 0):
            cv2.rectangle(frame, crosswalk_start, crosswalk_end, (255, 255, 0), 2)

        # Perform object detection using YOLOv5
        results = model(frame)
        labels = results.xyxy[0][:, -1].cpu().numpy()
        coordinates = results.xyxy[0][:, :-1].cpu().numpy()

        # Variable to track whether a person is detected crossing the road
        person_in_crosswalk = False

        for i in range(len(labels)):
            class_id = int(labels[i])

            # Check if the detected object is a person (class_id == 0 corresponds to 'person')
            if class_id == 0:
                x1, y1, x2, y2 = map(int, coordinates[i][:4])

                # Check if the bounding box of the person is inside the defined crosswalk area
                if (x1 > crosswalk_start[0] and y1 > crosswalk_start[1] and
                    x2 < crosswalk_end[0] and y2 < crosswalk_end[1]):
                    person_in_crosswalk = True
                    # Draw a red rectangle around the detected person
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        signal_x = int((crosswalk_start[0] + crosswalk_end[0]) / 2)  # Midpoint of the crosswalk for x   <-- CHANGE HERE
        signal_y = crosswalk_end[1] - 250 # Place the signal 50 pixels below the crosswalk  <-- CHANGE HERE

# Set the traffic signal based on whether a person is detected crossing the road
        if person_in_crosswalk:
            cv2.circle(frame, (signal_x, signal_y), 30, (0, 0, 255), -1)  # Draw red circle at signal location  <-- CHANGE HERE
        else:
    # Green traffic light (no human detected)
            cv2.circle(frame, (signal_x, signal_y), 30, (0, 255, 0), -1) 
        # Display the frame
        cv2.imshow('Crosswalk Detection', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return "Processing completed for video: " + filename

if __name__ == '__main__':
    # Ensure upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
