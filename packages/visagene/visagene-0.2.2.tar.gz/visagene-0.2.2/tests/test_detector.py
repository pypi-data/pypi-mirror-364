import os

import pixtreme as px
import tensorrt as trt

import visagene_source as vg


def test_face_detection():
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model
    model = vg.OnnxDetector(model_path="models/detection.onnx")

    faces = model.get(image)

    print(f"Detected {len(faces)} faces.")
    for i, face in enumerate(faces):
        print(f"type(face): {type(face)}")
        print(f"Face bbox: {face.bbox}, score: {face.score}, kps: {face.kps}, matrix: {face.matrix}")
        px.imshow(f"Onnx Detected Face {i}", face.image)

    engine = vg.TrtDetector(model_path="models/detection.onnx")
    faces_trt = engine.get(image)

    print(f"Detected {len(faces_trt)} faces (TensorRT).")
    for i, face in enumerate(faces_trt):
        print(f"type(face): {type(face)}")
        print(f"Face bbox: {face.bbox}, score: {face.score}, kps: {face.kps}, matrix: {face.matrix}")
        px.imshow(f"Trt Detected Face {i}", face.image)

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_detection()
