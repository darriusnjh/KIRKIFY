#!/bin/bash

# Script to download YOLO hand detection models
# Based on cansik/yolo-hand-detection repository

MODEL_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://github.com/cansik/yolo-hand-detection/releases/download/v1.0"

echo "Downloading YOLO hand detection models..."
echo "Models will be saved to: $MODEL_DIR"

# YOLOv3-tiny
echo "Downloading YOLOv3-tiny..."
curl -L -o "$MODEL_DIR/yolov3-tiny.weights" "$BASE_URL/yolov3-tiny.weights"
curl -L -o "$MODEL_DIR/yolov3-tiny.cfg" "$BASE_URL/yolov3-tiny.cfg"

# YOLOv3-tiny-PRN
echo "Downloading YOLOv3-tiny-PRN..."
curl -L -o "$MODEL_DIR/yolov3-tiny-prn.weights" "$BASE_URL/yolov3-tiny-prn.weights"
curl -L -o "$MODEL_DIR/yolov3-tiny-prn.cfg" "$BASE_URL/yolov3-tiny-prn.cfg"

# YOLOv4-tiny
echo "Downloading YOLOv4-tiny..."
curl -L -o "$MODEL_DIR/yolov4-tiny.weights" "$BASE_URL/yolov4-tiny.weights"
curl -L -o "$MODEL_DIR/yolov4-tiny.cfg" "$BASE_URL/yolov4-tiny.cfg"

# YOLOv3 (full)
echo "Downloading YOLOv3 (full)..."
curl -L -o "$MODEL_DIR/yolov3.weights" "$BASE_URL/yolov3.weights"
curl -L -o "$MODEL_DIR/yolov3.cfg" "$BASE_URL/yolov3.cfg"

# Download names file (classes)
echo "Downloading class names..."
curl -L -o "$MODEL_DIR/classes.names" "$BASE_URL/classes.names"

echo "Download complete!"
echo "Note: If downloads fail, you may need to download manually from:"
echo "https://github.com/cansik/yolo-hand-detection/releases"
