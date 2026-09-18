"""Regression tests for ComfyUI download URL encoding."""

from open_video.engines.comfyui.adapter import ComfyUIAdapter


def test_fetch_outputs_url_encodes_filename_and_subfolder(tmp_path, monkeypatch):
    adapter = ComfyUIAdapter(output_dir=str(tmp_path))

    captured = {}

    def fake_urlretrieve(url, path):
        captured["url"] = url

    monkeypatch.setattr("urllib.request.urlretrieve", fake_urlretrieve)
    monkeypatch.setattr(
        adapter,
        "_json",
        lambda *args, **kwargs: {
            "fake-id": {
                "outputs": {
                    "save_video": {
                        "videos": [
                            {
                                "filename": "my clip #1.mp4",
                                "subfolder": "shots/a&b",
                            }
                        ]
                    }
                }
            }
        },
    )

    adapter.fetch_outputs("fake-id")

    assert "filename=my+clip+%231.mp4" in captured["url"]
    assert "subfolder=shots%2Fa%26b" in captured["url"]
    assert "type=output" in captured["url"]
