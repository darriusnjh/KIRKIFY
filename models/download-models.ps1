# PowerShell script to download YOLO hand detection models
# Based on cansik/yolo-hand-detection repository

$MODEL_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BASE_URL = "https://github.com/cansik/yolo-hand-detection/releases/download/v1.0"

Write-Host "Downloading YOLO hand detection models..."
Write-Host "Models will be saved to: $MODEL_DIR"

# YOLOv3-tiny
Write-Host "Downloading YOLOv3-tiny..."
Invoke-WebRequest -Uri "$BASE_URL/yolov3-tiny.weights" -OutFile "$MODEL_DIR\yolov3-tiny.weights"
Invoke-WebRequest -Uri "$BASE_URL/yolov3-tiny.cfg" -OutFile "$MODEL_DIR\yolov3-tiny.cfg"

# YOLOv3-tiny-PRN
Write-Host "Downloading YOLOv3-tiny-PRN..."
Invoke-WebRequest -Uri "$BASE_URL/yolov3-tiny-prn.weights" -OutFile "$MODEL_DIR\yolov3-tiny-prn.weights"
Invoke-WebRequest -Uri "$BASE_URL/yolov3-tiny-prn.cfg" -OutFile "$MODEL_DIR\yolov3-tiny-prn.cfg"

# YOLOv4-tiny
Write-Host "Downloading YOLOv4-tiny..."
Invoke-WebRequest -Uri "$BASE_URL/yolov4-tiny.weights" -OutFile "$MODEL_DIR\yolov4-tiny.weights"
Invoke-WebRequest -Uri "$BASE_URL/yolov4-tiny.cfg" -OutFile "$MODEL_DIR\yolov4-tiny.cfg"

# YOLOv3 (full)
Write-Host "Downloading YOLOv3 (full)..."
Invoke-WebRequest -Uri "$BASE_URL/yolov3.weights" -OutFile "$MODEL_DIR\yolov3.weights"
Invoke-WebRequest -Uri "$BASE_URL/yolov3.cfg" -OutFile "$MODEL_DIR\yolov3.cfg"

# Download names file (classes)
Write-Host "Downloading class names..."
Invoke-WebRequest -Uri "$BASE_URL/classes.names" -OutFile "$MODEL_DIR\classes.names"

Write-Host "Download complete!"
Write-Host "Note: If downloads fail, you may need to download manually from:"
Write-Host "https://github.com/cansik/yolo-hand-detection/releases"
