from noahs_google_drive_downloader import download_google_drive_folder, download_google_drive_file
import subprocess
import os
import sys

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2





def load_pose_landmarker(output_path="pose_landmarker.task"):
	try:
		download_google_drive_file(
			url="https://drive.google.com/file/d/1uwTK3BKFtthZLme93nDFFETEZxrKpnOZ/view?usp=sharing",
			output_path=output_path
		)
	except:
		print("noahs_google_drive_downloader WARNING: unable to download pose_landmarker.task")




def draw_landmarks_on_image(rgb_image, detection_result):
	# Convert RGB image to BGR for OpenCV display or saving
	bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
	annotated_image = np.copy(bgr_image)

	pose_landmarks_list = detection_result.pose_landmarks

	# Loop over each detected person's pose landmarks
	for idx in range(len(pose_landmarks_list)):
		pose_landmarks = pose_landmarks_list[idx]

		# Convert landmarks to protobuf format
		pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
		pose_landmarks_proto.landmark.extend([
			landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
		])

		# Draw landmarks and connections on the image
		solutions.drawing_utils.draw_landmarks(
			annotated_image,
			pose_landmarks_proto,
			solutions.pose.POSE_CONNECTIONS,  # predefined pose skeleton connections
			solutions.drawing_styles.get_default_pose_landmarks_style()
		)

	# RETURN: the original image overlaid with pose landmarks in BGR format (for saving or display)
	return annotated_image




def draw_landmarks(rgb_image, detection_result):
	# Create a black canvas with same shape as input image
	height, width, _ = rgb_image.shape
	black_background = np.zeros((height, width, 3), dtype=np.uint8)

	pose_landmarks_list = detection_result.pose_landmarks

	# Draw pose landmarks on the black background
	for idx in range(len(pose_landmarks_list)):
		pose_landmarks = pose_landmarks_list[idx]

		pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
		pose_landmarks_proto.landmark.extend([
			landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
		])

		solutions.drawing_utils.draw_landmarks(
			black_background,
			pose_landmarks_proto,
			solutions.pose.POSE_CONNECTIONS,
			solutions.drawing_styles.get_default_pose_landmarks_style()
		)

	# RETURN: a black image showing only the drawn pose landmarks (no background)
	return black_background










class PoseDetector:
	def __init__(self, detector_file="pose_landmarker.task"):
		load_pose_landmarker(detector_file)
		self.base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
		self.options = vision.PoseLandmarkerOptions(base_options=self.base_options, output_segmentation_masks=True)
		self.detector = vision.PoseLandmarker.create_from_options(self.options)

	def get_pose(self, image_file="image.jpg"):
		# Load the image into MediaPipe's Image format
		image = mp.Image.create_from_file(image_file)

		# Run pose detection
		detection_result = self.detector.detect(image)

		# RETURN:
		# - image: MediaPipe Image object (RGB)
		# - detection_result: result object containing pose landmarks and segmentation mask
		return image, detection_result

	def add_pose_on_top_of_image(self, image_file="image.jpg", output_file="image_with_pose.jpg"):
		# Load original image using OpenCV (BGR format)
		original_image = cv2.imread(image_file)

		# Convert to RGB format for MediaPipe processing
		original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

		# Run pose detection
		image, detection_result = self.get_pose(image_file)

		# Draw landmarks on top of the original image
		annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)

		# Save the result to a file
		cv2.imwrite(output_file, annotated_image)

		# RETURN: image with landmarks drawn over it (in BGR format)
		return annotated_image

	def convert_image_to_pose(self, image_file="image.jpg", output_file="image_pose.jpg"):
		# Load original image using OpenCV (BGR format)
		original_image = cv2.imread(image_file)

		# Convert to RGB for MediaPipe
		original_image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

		# Run pose detection
		image, detection_result = self.get_pose(image_file)

		# Draw only pose landmarks on black background
		annotated_image = draw_landmarks(image.numpy_view(), detection_result)

		# Save to file
		cv2.imwrite(output_file, annotated_image)

		# RETURN: a black image with pose landmarks drawn (in BGR format)
		return annotated_image

	def convert_image_to_mask(self, image_file="image.jpg", output_file="image_mask.jpg", inverse=False):
		"""
		Converts an input image to a MediaPipe segmentation mask.

		Parameters:
			image_file (str): Path to the input image.
			output_file (str): Path to save the generated mask image.
			inverse (bool): If True, inverts the segmentation mask (background becomes foreground and vice versa).

		Returns:
			visualized_mask (np.ndarray): The final 3-channel mask as a NumPy array (uint8, values 0-255).
		"""
		# Run pose detection
		image, detection_result = self.get_pose(image_file)

		# Extract the segmentation mask for the first detected pose
		segmentation_mask = detection_result.segmentation_masks[0].numpy_view()  # shape: (H, W), values in [0.0, 1.0]

		if inverse:
			# Invert the mask: foreground becomes background
			segmentation_mask = 1.0 - segmentation_mask

		# Convert to 3-channel grayscale mask for visualization
		visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2) * 255

		# Save to output file
		cv2.imwrite(output_file, visualized_mask.astype(np.uint8))

		# RETURN: 3-channel uint8 grayscale image showing the (optionally inverted) mask
		return visualized_mask


	def get_pose_points(self, image_file="image.jpg"):
		"""
		Detects pose landmarks in the input image (either a file path or bytes) and returns a dictionary
		mapping landmark names to pixel coordinates.

		Parameters:
			image_file (str or bytes): Path to the input image or raw image bytes.

		Returns:
			dict: A dictionary like {"left knee": (x, y), "right shoulder": (x, y)}, where
				  x and y are pixel coordinates of the detected landmark.
		"""
		# Load image from path or bytes
		if isinstance(image_file, bytes):
			# Convert bytes to a NumPy array
			nparr = np.frombuffer(image_file, np.uint8)
			img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # BGR image
			img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
			image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
		elif isinstance(image_file, str):
			image = mp.Image.create_from_file(image_file)
		else:
			raise ValueError("image_file must be a file path (str) or image bytes (bytes)")

		# Run pose detection
		detection_result = self.detector.detect(image)

		# Get image dimensions
		image_height, image_width = image.numpy_view().shape[:2]

		# Define mapping from MediaPipe landmark indices to human-readable names
		landmark_names = solutions.pose.PoseLandmark

		# Get the first detected pose landmarks (if any)
		if not detection_result.pose_landmarks:
			return {}  # No pose detected

		pose_landmarks = detection_result.pose_landmarks[0]  # First person's pose

		# Create a dictionary of {landmark_name: (x_pixel, y_pixel)}
		pose_points = {}
		for idx, landmark in enumerate(pose_landmarks):
			name = landmark_names(idx).name
			x_px = int(landmark.x * image_width)
			y_px = int(landmark.y * image_height)
			pose_points[name] = (x_px, y_px)

		return pose_points



	def render_pose_from_points(self, pose_points, image_size=(480, 640), output_file="rendered_pose.jpg"):
		"""
		Renders pose landmarks on a blank image from a given dictionary of pose points.

		Parameters:
			pose_points (dict): A dictionary of {"landmark name": (x, y)} pixel coordinates.
			image_size (tuple): Size of the image as (height, width). Defaults to (480, 640).
			output_file (str): File path to save the rendered image.

		Returns:
			np.ndarray: The image with pose landmarks rendered.
		"""

		height, width = image_size

		# Create a blank black image
		image = np.zeros((height, width, 3), dtype=np.uint8)

		# Get enum for landmark names for reverse lookup
		pose_landmark_enum = solutions.pose.PoseLandmark

		# Build a list with 33 landmark positions in correct order (some may be missing)
		landmarks = []
		for i in range(len(pose_landmark_enum)):
			name = pose_landmark_enum(i).name
			if name in pose_points:
				x, y = pose_points[name]
				# Normalize coordinates back to [0, 1] for MediaPipe input
				normalized_x = x / width
				normalized_y = y / height
				landmarks.append(landmark_pb2.NormalizedLandmark(x=normalized_x, y=normalized_y, z=0.0))
			else:
				# If the point is missing, use a dummy point out of bounds
				landmarks.append(landmark_pb2.NormalizedLandmark(x=0.0, y=0.0, z=0.0))

		# Wrap the landmarks into a NormalizedLandmarkList
		landmark_list = landmark_pb2.NormalizedLandmarkList(landmark=landmarks)

		# Draw the landmarks on the image
		solutions.drawing_utils.draw_landmarks(
			image,
			landmark_list,
			solutions.pose.POSE_CONNECTIONS,
			solutions.drawing_styles.get_default_pose_landmarks_style()
		)

		# Save the result
		cv2.imwrite(output_file, image)

		return image






	def get_face_direction_from_pose_points(self, pose_points, threshold=0.15, perspective="1st"):
		"""
		Estimate if the face is looking LEFT, RIGHT, or CENTER based on spacing between eye landmarks.

		Parameters:
			pose_points (dict): Dictionary from `get_pose_points()` with pixel coordinates.
			threshold (float): Normalized threshold (0.0 - 1.0) for deciding face direction.
							   Higher values make the function more strict about declaring LEFT/RIGHT.

		Returns:
			str: One of "LEFT", "RIGHT", or "CENTER"
		"""

		# Check if all required landmarks are available
		required_keys = ["LEFT_EYE_INNER", "LEFT_EYE", "LEFT_EYE_OUTER",
						 "RIGHT_EYE_INNER", "RIGHT_EYE", "RIGHT_EYE_OUTER"]
		if not all(key in pose_points for key in required_keys):
			return "UNKNOWN"

		# Calculate horizontal (x) distances
		left_eye_width = abs(pose_points["LEFT_EYE_OUTER"][0] - pose_points["LEFT_EYE_INNER"][0])
		right_eye_width = abs(pose_points["RIGHT_EYE_OUTER"][0] - pose_points["RIGHT_EYE_INNER"][0])

		# Normalize widths by average to make comparison relative
		avg_eye_width = (left_eye_width + right_eye_width) / 2
		if avg_eye_width == 0:
			return "UNKNOWN"

		left_ratio = left_eye_width / avg_eye_width
		right_ratio = right_eye_width / avg_eye_width

		answer = None

		# Compare ratios: the more compressed side likely indicates where the person is *facing toward*
		if left_ratio < (1 - threshold) and right_ratio > (1 + threshold):
			answer = "LEFT"   # Left eye is scrunched = looking left
		elif right_ratio < (1 - threshold) and left_ratio > (1 + threshold):
			answer = "RIGHT"  # Right eye is scrunched = looking right
		else:
			answer = "CENTER"

		if perspective == "1st":
			return answer
		else:
			if answer == "LEFT":
				return "RIGHT"
			elif answer == "RIGHT":
				return "LEFT"
			else:
				return "CENTER"




















if __name__ == "__main__":

	# instantiate Pose Detector object
	d = PoseDetector()

	# generating pose masks and inverse pose masks from images
	# greate for creating mask for the main character or background
	mask = d.convert_image_to_mask("image.jpg","image_mask.jpg")
	mask = d.convert_image_to_mask("image.jpg","image_mask_inverse.jpg",inverse=True)

	# generate an image of the pose with a black background
	pose = d.convert_image_to_pose("image.jpg","image_pose.jpg")

	# generate an image of the pose on top of the original image
	image_with_pose = d.add_pose_on_top_of_image("image.jpg","image_with_pose.jpg")

	# extract pose point locations and then generate the pose image from points
	points = d.get_pose_points("image.jpg")
	points_image = d.render_pose_from_points(points, image_size=(640,960), output_file="image_rendered_pose.jpg")

	# extract pose point locations then determine face orientation based on them
	# perspective = "3rd" means direction will be from the camera's perspective
	# perspective = "1st" means the direction will be from the subject's perspecive
	points = d.get_pose_points("image.jpg")
	direction1 = d.get_face_direction_from_pose_points(points,threshold=0.15, perspective="3rd")
	print(f"Face 1 is facing: {direction1}")

	points2 = d.get_pose_points("image2.jpg")
	direction2 = d.get_face_direction_from_pose_points(points2,threshold=0.15, perspective="3rd")
	print(f"Face 2 is facing: {direction2}")

	points3 = d.get_pose_points("image3.jpg")
	direction3 = d.get_face_direction_from_pose_points(points3,threshold=0.15, perspective="3rd")
	print(f"Face 3 is facing: {direction3}")


	# the get_pose_points method can also be used on image bytes directly
	with open("image.jpg", "rb") as f:
		image_bytes = f.read()
	pose_points_from_bytes = d.get_pose_points(image_bytes)
	print(pose_points_from_bytes)

















































