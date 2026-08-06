# LoRA Recipe: [Your LoRA Name]

> A LoRA recipe is the structured record of a community-trained H3 LoRA. Copy this template, fill
> every field in, save as `library/loras/<category>/<your_name>__<slug>.md`, and PR. The weights
> themselves are **not** committed — host them on HF / Civitai / your own host and link them in
> `weights_url`. See `docs/library-and-loras.md` for the full guide.

## Metadata
- **id:** `acme/my_character`            <!-- lowercase org/slug; this is what users pass as --lora -->
- **category:** character                <!-- one of: cinematic | anime | product | character | style -->
- **tags:** [cinematic, hero-shot]       <!-- secondary tags for search/filtering -->
- **author:** [your handle / org]
- **license:** Apache-2.0                <!-- must match the weights' actual license -->
- **license_restricted:** false          <!-- true if commercial/exclusive-restricted -->
- **base_model:** MiniMax H3 (int8 ConvRot, Comfy-Org)   <!-- which backbone it was trained against -->
- **weights_url:** https://huggingface.co/<you>/<this-lora>/resolve/main/my_character.safetensors
- **weights_size_mb:** 180               <!-- round number, helps users budget -->

## Training
- **method:** Inline Studio QLoRA        <!-- Inline Studio QLoRA (static appearance) | musubi-tuner video LoRA (motion, R2 FP8) -->
- **training_repo_url:** https://github.com/<inline-studio-or-musubi-tuner>   <!-- the trainer you used -->
- **dataset_summary:** 42 reference frames (1 subject, varied angle/lighting/wardrobe-stable), captioned with the trigger word
- **dataset_consent:** all images taken with subject's written consent (on file); no third-party likenesses <!-- REQUIRED: source + consent status -->
- **steps:** 1500
- **gpu:** RTX 5090
- **vram_gb:** 21                        <!-- observed peak VRAM -->
- **training_time_h:** ~3.5
- **trigger_word:** `mychr`              <!-- the token that activates the LoRA at inference; must appear in example_prompt -->

## Usage
- **recommended_strength:** 0.8          <!-- video LoRAs usually 0.6–0.9; tune in 0.05 steps -->
- **stacks_with:** [style/studio_grade, cinematic/anamorphic35mm]   <!-- other LoRAs this is known to compose cleanly with -->
- **known_issues:** at strength > 1.0 the skin tone shifts magenta; drop to 0.7
- **example_prompt:**                    <!-- H3 3-field, copy-paste ready, MUST contain the trigger word -->

<!-- trigger word `mychr` appears below: -->
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium shot frames mychr,
the lighthouse keeper, as she scans the horizon. The camera pushes in with small amplitude at slow
speed as the wind tugs at her coat.

overall_soundscape: wind and distant waves against weathered stone, the soft creak of a lantern in the gusts.

non_diegetic_music: a solo cello sustains a low note, slow tempo, against a faint sustained pad.

- **tips:**
  - Pair with `library/reference_packs/lighthouse_keeper/` for cross-shot identity lock.
  - Works best at 1344×768, 20 steps, sage attention.
  - If the face drifts on the 2nd chained shot, raise strength to 0.85 only for shot 1 (anchor).

## Before / after (same seed + prompt — trigger only in "after")
- **Seed:** 12345
- **Prompt (without trigger):** a medium shot frames a lighthouse keeper, the camera pushes in… <!-- identical minus the trigger word -->
- **Before (no LoRA):** https://<your-host>/before.mp4   <!-- or .png keyframe -->
- **After (with LoRA + trigger):** https://<your-host>/after.mp4
- **Observed effect:** locks the keeper's face + wardrobe across re-rolls; without the LoRA H3
  produces a different keeper every seed.

<!-- The before/after pair is the proof the LoRA does something. Indistinguishable pairs get sent
     back at review. -->

## Consent & provenance
- **dataset_source:** original photography by the contributor + subject
- **consent_status:** written consent on file from the depicted subject
- **third_party_likenesses:** none
- **usage_restrictions:** none beyond the license above
