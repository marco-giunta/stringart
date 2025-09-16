# import pytest
# import numpy as np
# from pathlib import Path
# from PIL import Image
# from stringart import cli

# def make_dummy_image(path):
#     arr = (np.ones((10, 10, 3)) * 255).astype(np.uint8)  # white 10x10 RGB
#     Image.fromarray(arr).save(path)

# def test_cli_parsing_and_create_stringart_called(monkeypatch, tmp_path):
#     """Ensure CLI calls create_stringart with correct args."""
#     dummy_img = tmp_path / "img.png"
#     make_dummy_image(dummy_img)


#     called = {}

#     def fake_create_stringart(**kwargs):
#         called.update(kwargs)
#         return np.array([0, 1]), np.zeros((10, 10)), np.array([0.1, 0.010])

#     monkeypatch.setattr(cli, "create_stringart", fake_create_stringart)
#     monkeypatch.setattr(cli, "imshow", lambda x: None)
#     monkeypatch.setattr(cli, "show", lambda: None)
#     monkeypatch.setattr(cli, "save_stringart", lambda arr, path: None)

#     argv = [
#         "-i", str(dummy_img),
#         "-n", "10",
#         "-d", "1.0",
#         "-o", str(tmp_path / "out.png"),
#         "-so", str(tmp_path / "order.txt"),
#         "-ds", str(tmp_path / "dist.txt"),
#     ]

#     cli.stringart_cli(argv)

#     # Validate arguments passed through
#     assert called["img_path"] == str(dummy_img)
#     assert called["num_nails"] == 10
#     assert called["downscale_factor"] == 1.0


# def test_cli_invalid_output_extension(monkeypatch, tmp_path):
#     """Ensure invalid extension raises ValueError."""
#     dummy_img = tmp_path / "img.png"
#     make_dummy_image(dummy_img)


#     monkeypatch.setattr(cli, "create_stringart", lambda **_: ([], np.zeros((10, 10)), []))
#     monkeypatch.setattr(cli, "imshow", lambda x: None)
#     monkeypatch.setattr(cli, "show", lambda: None)

#     argv = [
#         "-i", str(dummy_img),
#         "-n", "10",
#         "-d", "1.0",
#         "-o", str(tmp_path / "bad_output.xyz"),  # unsupported extension
#     ]

#     with pytest.raises(ValueError, match="Unsupported extension"):
#         cli.stringart_cli(argv)
