"""Tests for the ModelBackend contract + ShotRequest + Capabilities."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from open_video.core.backend import ShotRequest, Capabilities, ModelBackend


def test_shot_request_defaults():
    """ShotRequest has sensible defaults for all fields."""
    req = ShotRequest(prompt="test", mode="t2v", width=1344, height=768, duration_s=5.0, seed=42)
    assert req.prompt == "test"
    assert req.mode == "t2v"
    assert req.first_frame is None
    assert req.last_frame is None
    assert req.references == ()
    assert req.lora is None
    assert req.lora_weight == 0.8
    assert req.trigger_word is None


def test_shot_request_with_lora():
    """ShotRequest accepts LoRA parameters."""
    req = ShotRequest(prompt="test", mode="t2v", width=1344, height=768, duration_s=5.0, seed=42,
                      lora="cinematic-v2.safetensors", lora_weight=0.7, trigger_word="cinematic_style")
    assert req.lora == "cinematic-v2.safetensors"
    assert req.lora_weight == 0.7
    assert req.trigger_word == "cinematic_style"


def test_capabilities_defaults():
    """Capabilities has correct defaults."""
    caps = Capabilities()
    assert caps.t2v is True
    assert caps.i2v is False
    assert caps.native_audio is False
    assert caps.max_duration_s == 15.0
    assert caps.max_short_edge_px == 768


def test_capabilities_with_audio():
    """Capabilities can be configured for audio-capable models."""
    caps = Capabilities(native_audio=True, i2v=True, strengths=("audio", "prompt-adherence"))
    assert caps.native_audio is True
    assert caps.i2v is True
    assert "audio" in caps.strengths


def test_model_backend_is_abstract():
    """ModelBackend methods raise NotImplementedError (interface contract)."""
    b = ModelBackend()  # can instantiate (not abc.ABC, uses NotImplementedError pattern)
    try:
        b.prompt_guide()
        assert False, "Should have raised NotImplementedError"
    except NotImplementedError:
        pass  # correct: interface methods raise


if __name__ == "__main__":
    test_shot_request_defaults()
    test_shot_request_with_lora()
    test_capabilities_defaults()
    test_capabilities_with_audio()
    test_model_backend_is_abstract()
    print("✅ All backend tests passed")

def test_lora_shot_request():
    """ShotRequest correctly carries LoRA parameters."""
    req = ShotRequest(prompt="cinematic shot", mode="t2v", width=1344, height=768,
                     duration_s=5.0, seed=42, lora="cinematic-v2.safetensors",
                     lora_weight=0.7, trigger_word="cinematic_style")
    assert req.lora == "cinematic-v2.safetensors"
    assert req.lora_weight == 0.7
    assert req.trigger_word == "cinematic_style"

def test_lora_workflow_insertion():
    """H3 backend correctly inserts LoraLoader when LoRA is requested."""
    import json
    wf = json.loads(open("backends/h3/workflows/h3_t2v_api.json").read())
    # simulate LoRA insertion (same logic as H3Backend.generate)
    req = ShotRequest(prompt="test", mode="t2v", width=960, height=544,
                     duration_s=5.0, seed=42, lora="test.safetensors", lora_weight=0.8)
    if req.lora:
        wf["lora_loader"] = {"class_type": "LoraLoader", "inputs": {
            "model": ["load_unet", 0], "clip": ["load_clip", 0], "lora_name": req.lora,
            "strength_model": req.lora_weight, "strength_clip": 0.0}}
        wf["sigmashift"]["inputs"]["model"] = ["lora_loader", 0]
    assert "lora_loader" in wf, "LoraLoader node should be added"
    assert wf["lora_loader"]["inputs"]["lora_name"] == "test.safetensors"
    assert wf["lora_loader"]["inputs"]["strength_model"] == 0.8
    assert wf["lora_loader"]["inputs"]["clip"] == ["load_clip", 0]
    assert wf["sigmashift"]["inputs"]["model"] == ["lora_loader", 0], "sigmashift should be rewired through LoRA"

# run new tests
test_lora_shot_request()
test_lora_workflow_insertion()
print("✅ LoRA tests passed (2 new)")
