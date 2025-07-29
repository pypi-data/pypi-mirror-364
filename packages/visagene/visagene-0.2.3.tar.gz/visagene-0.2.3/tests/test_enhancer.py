import pixtreme as px

import visagene_source as vg


def test_face_enhancement():
    # Load a test image
    image = px.imread("examples/example.png")
    image = px.to_float32(image)

    # Initialize the face detection model to get faces first
    detector = vg.OnnxDetector(model_path="models/detection.onnx")
    faces = detector.get(image, crop_size=512)
    big_faces = detector.get(image, crop_size=1024)

    assert len(faces) > 0, "No faces detected for enhancement test."
    assert len(big_faces) > 0, "No big faces detected for enhancement test."

    print(f"Found {len(faces)} faces for enhancement.")

    # Initialize the face enhancement model
    enhancer = vg.OnnxEnhancer(model_path="models/GFPGANv1.4.onnx")

    for i, face in enumerate(faces):
        print(f"\nProcessing Face {i}:")
        print(f"Face bbox: {face.bbox}, score: {face.score}")
        print(f"Original face image shape: {face.image.shape}")
        print(f"Face image dtype: {face.image.dtype}")

        # Test single face enhancement
        print("Testing single face enhancement...")
        enhanced_face = enhancer.get(face.image)

        # Test batch enhancement (multiple same images)
        # print("Testing batch enhancement...")
        # batch_enhanced = enhancer.get([face.image, face.image])
        # if isinstance(batch_enhanced, list):
        #    print(f"Batch enhanced: {len(batch_enhanced)} images")
        # else:
        #    print(f"Batch enhanced shape: {batch_enhanced.shape}")

        # Test subpixel enhancement (higher quality)
        print("Testing subpixel enhancement...")
        subpixel_enhanced = enhancer.get_subpixel(big_faces[i].image)
        print(f"Subpixel enhanced shape: {subpixel_enhanced.shape}")

        # Display results
        px.imshow(f"Original Face {i}", face.image)
        px.imshow(f"Enhanced Face {i}", enhanced_face)
        px.imshow(f"Subpixel Enhanced Face {i}", subpixel_enhanced)

        print(f"Full image enhanced shape: {enhanced_face.shape}")

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_face_enhancement()
