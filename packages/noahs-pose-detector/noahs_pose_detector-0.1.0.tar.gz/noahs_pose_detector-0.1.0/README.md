# Pose Detection Utility with MediaPipe

This project provides a Python utility for pose detection and analysis using MediaPipe's `PoseLandmarker` model. It supports loading pose detection models, extracting and visualizing pose landmarks, creating segmentation masks, estimating face direction, and working with image files directly or as bytes.

## Features

* Automatically downloads the pose detection model
* Detects human pose landmarks in static images
* Overlays pose landmarks on original or black background images
* Creates segmentation masks (foreground/background)
* Extracts pose landmark coordinates
* Reconstructs poses from landmark coordinates
* Estimates face direction (LEFT, RIGHT, CENTER)

## Dependencies

* mediapipe
* opencv-python
* numpy

---

## Installation

```bash
pip install noahs_pose_detector
```

---

## Example Usage

```python
from noahs_pose_detector import PoseDetector

# instantiate Pose Detector object
d = PoseDetector()

# generating pose masks and inverse pose masks from images
# great for creating mask for the human subject or background
mask = d.convert_image_to_mask("image.jpg","image_mask.jpg")
mask = d.convert_image_to_mask("image.jpg","image_mask_inverse.jpg",inverse=True)

# generate an image of the pose points with a black background
pose = d.convert_image_to_pose("image.jpg","image_pose.jpg")

# generate an image of the pose points on top of the original image
image_with_pose = d.add_pose_on_top_of_image("image.jpg","image_with_pose.jpg")

# extract pose point locations and then generate the pose image from extracted points
points = d.get_pose_points("image.jpg")
points_image = d.render_pose_from_points(points, image_size=(640,960), output_file="image_rendered_pose.jpg")

# extract pose point locations then determine face orientation based on them
# perspective = "3rd" means direction will be from the camera's perspective
# perspective = "1st" means the direction will be from the subject's perspective
# possible direction outputs are (LEFT, RIGHT, CENTER)
direction = d.get_face_direction_from_pose_points(points,threshold=0.15, perspective="3rd")
print(f"Face is facing: {direction}")


# the get_pose_points method can also be used on image bytes directly
with open("image.jpg", "rb") as f:
	image_bytes = f.read()
pose_points_from_bytes = d.get_pose_points(image_bytes)
print(pose_points_from_bytes)
```

---

## Notes

* Uses a helper module `noahs_google_drive_downloader` to download the model asset from Google Drive.
* Assumes the `pose_landmarker.task` file is downloaded or available in the working directory.
* The segmentation mask is returned as a 3-channel grayscale image for easy visualization.
* This script is ideal for gesture analysis
