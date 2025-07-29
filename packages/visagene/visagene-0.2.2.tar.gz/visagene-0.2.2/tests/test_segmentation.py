import os

import cupy as cp
import pixtreme as px

import visagene_source as vg


def test_segmentation():
    # Initialize the segmentation model
    model_path = "models/convnext_celeba_512_model_299.onnx"
    model = vg.OnnxSegmentation(model_path=model_path)

    # Load a test image
    image_path = "examples/example2.png"
    image = px.imread(image_path)
    image = px.to_float32(image)
    image = px.resize(image, (512, 512), interpolation=px.INTER_AUTO)

    px.imshow("Input Image", image)

    # まず、モデルの再現性を確認
    print("\n=== モデルの再現性確認 ===")
    mask_single1 = model.get(image)
    mask_single2 = model.get(image)

    is_deterministic = cp.allclose(mask_single1, mask_single2, rtol=1e-5, atol=1e-5)
    max_diff_single = cp.max(cp.abs(mask_single1 - mask_single2))
    diff_count_single = cp.sum(cp.abs(mask_single1 - mask_single2) > 1e-5)

    print(f"Single vs Single (同じ画像を2回処理):")
    print(f"  - Equal: {is_deterministic}")
    print(f"  - Max absolute difference: {max_diff_single}")
    print(
        f"  - Different pixels: {diff_count_single}/{mask_single1.size} ({float(diff_count_single) / mask_single1.size * 100:.4f}%)"
    )

    # 単体のgetメソッドで処理（以降はmask_single1を使用）
    mask_single = mask_single1
    px.imshow("Single Segmentation Mask", mask_single)

    # 同一画像をバッチで処理
    masks_batch = model.batch_get([image, image, image])

    # 結果の比較
    print("\n=== 単体get()とbatch_get()の結果比較 ===")

    # バッチ処理の各結果と単体処理の結果を比較
    for i, mask_batch in enumerate(masks_batch):
        # CuPyアレイの比較（より寛容な許容誤差を設定）
        is_equal = cp.allclose(mask_single, mask_batch, rtol=0.01, atol=0.01)
        max_diff = cp.max(cp.abs(mask_single - mask_batch))

        # 差異のあるピクセル数をカウント
        diff_count = cp.sum(cp.abs(mask_single - mask_batch) > 1e-5)
        total_pixels = mask_single.size

        print(f"Batch mask {i} vs Single mask:")
        print(f"  - Shape single: {mask_single.shape}, batch: {mask_batch.shape}")
        print(f"  - Equal (within tolerance): {is_equal}")
        print(f"  - Max absolute difference: {max_diff}")
        print(f"  - Different pixels: {diff_count}/{total_pixels} ({float(diff_count) / total_pixels * 100:.2f}%)")

        # 差分画像を表示
        diff_image = cp.abs(mask_single - mask_batch)
        px.imshow(f"Difference {i}", diff_image)

        px.imshow(f"Batch Mask {i}", mask_batch)

    # 異なる画像でもテスト
    print("\n=== 異なる画像でのバッチ処理テスト ===")

    # 別の画像を読み込み
    image2_path = "examples/example1.png" if os.path.exists("examples/example1.png") else image_path
    image2 = px.imread(image2_path)
    image2 = px.to_float32(image2)
    image2 = px.resize(image2, (512, 512), interpolation=px.INTER_AUTO)

    # 混合バッチ処理
    mixed_masks = model.batch_get([image, image2, image])
    print(f"Mixed batch processed: {len(mixed_masks)} masks")

    # 大きなバッチサイズのテスト（バッチ分割処理の確認）
    print("\n=== 大きなバッチサイズのテスト ===")
    large_batch = [image] * 20  # MAX_BATCH_SIZE=16を超える
    large_masks = model.batch_get(large_batch)
    print(f"Large batch (20 images) processed: {len(large_masks)} masks")

    # 最初と最後の結果が単体処理と一致するか確認
    is_first_equal = cp.allclose(mask_single, large_masks[0], rtol=1e-5, atol=1e-5)
    is_last_equal = cp.allclose(mask_single, large_masks[-1], rtol=1e-5, atol=1e-5)
    print(f"First mask equal to single: {is_first_equal}")
    print(f"Last mask equal to single: {is_last_equal}")

    px.waitkey(0)
    px.destroy_all_windows()


if __name__ == "__main__":
    test_segmentation()
