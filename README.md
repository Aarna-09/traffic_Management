# Traffic Management System 🚦

This project is a traffic management system that uses computer vision to detect and analyze traffic flow from video inputs using a YOLOv5 model.

## 📁 Project Structure

.
├── detect.py # Main script for traffic detection
├── requirements.txt # Python dependencies
├── environment.yml # Conda environment configuration
├── templates/
│ └── upload.html # Upload form for video files
├── uploads/
│ ├── video3.mp4
│ ├── video4.mp4
│ ├── video6.mp4
│ └── video7.mp4
├── yolov5s.pt # YOLOv5 model weights

## 🚀 Features

- Upload and process traffic videos
- Real-time detection using YOLOv5
- Pretrained model (`yolov5s.pt`) included
- Web interface for video upload

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Aarna-09/traffic_Management.git
   cd traffic_Management
Create a virtual environment and install dependencies:

Using requirements.txt:
pip install -r requirements.txt


Or using Conda:
conda env create -f environment.yml
conda activate traffic_env
