# open-video — Plugin Registry & Marketplace Spec

> **Status:** v0 / spec (design). Implementation tracks Phase 1–3 in `PLAN.md`. Apache-2.0.
> **Audience:** plugin authors (model/backend, judge, engine, LoRA, recipe contributors), platform
> engineers wiring the registry client + index, and the review council that curates it.
> **One-line summary:** an `open-video install <plugin>` command plus a community-curated registry
> that makes models, judges, engines, LoRAs, and recipes as easy to find and install as `npm install`
> or `ollama pull` — the marketplace foundation.

---

## 0. What this is, and what we studied

open-video is pluggable by design: the **core** (planner / crafter / validator / judge / stitcher) is
model-agnostic and talks to models through the `ModelBackend` contract (`core/backend.py`), to engines
through the `EngineAdapter` contract, and to LoRAs through `ShotRequest.extra["lora"]` (see
`docs/library-and-loras.md` §4). Today you add a model by hand-dropping `backends/<name>/backend.py`
and editing `BACKEND_REGISTRY` in `cli/open_video.py`. The registry turns that into one command.

This spec is the marketplace foundation. It is **synthesized, not copied**, from three reference
systems whose tradeoffs we weighed:

| System | What we took | What we deliberately did differently |
|---|---|---|
| **ComfyUI Manager** + **ComfyUI Registry** (`registry.comfy.org`) | Community-curated `custom-node-list.json` updated by PR; `scanner.py` auto-derives the node map + GitHub stats; tiered `security_level` (strong/normal/normal-/weak); decoupled `allow_git_url_install` / `allow_pip_install` flags that only apply on loopback; **immutable published versions** ("once published, cannot be changed"); "deprecate a version" for takedown; scanner flags custom pip wheels + arbitrary system calls. | Flat `<publisher>/<name>` (not `@scope/name`) to stay language-agnostic and match the LoRA `id` convention already in the repo; one manifest schema for **all five plugin types** (ComfyUI's registry is custom-node-only); weights are content-addressed SHA256 blobs (ComfyUI relies on its default-channel trust). |
| **npm** (`package.json` + `registry.npmjs.org`) | The field vocabulary (`name`/`version`/`description`/`author`/`license`/`homepage`/`bugs`/`keywords`); semver range resolution + `latest` dist-tag; `peerDependencies` for host compatibility; `engines` for runtime constraints; `npm ci`-style frozen installs; scoped names for publisher namespaces; per-package download counts. | No JS-toolchain assumptions; install backends are git/tarball/HF, not `node_modules`; trusted-publisher "ratchet" replaces npm's raw publish-token model for code plugins. |
| **Ollama** (`Modelfile` + `registry.ollama.ai`) | `namespace/model:tag` names with `library/` as the implicit official namespace; `FROM <base>` layering so a LoRA can declare the backbone it sits on; **SHA256 content-addressed blobs + manifests** so weights are verifiable and resumable; pull resumes on cancel; derived models reuse base layers. | We don't run a registry server of our own for v0 — the index is a signed JSON file in a GitHub repo (the ComfyUI-Manager model), and weights live on HF/Civitai (the existing LoRA convention, `docs/library-and-loras.md` §6). |

The registry is also the **distribution surface** for the library flywheel described in
`docs/library-and-loras.md` (prompts, LoRAs, reference packs, coherence recipes) — so it must cover
metadata-only assets, not just code.

### Goals
1. **One-command install** for all five plugin types: `open-video install <publisher>/<name>`.
2. **A single manifest schema** that describes any plugin and is the contract between author,
   registry, scanner, installer, and the runtime that loads the plugin.
3. **A community-curated index** (GitHub PR review + automated scan) at `open-video.ai/registry`,
   with an official channel (`openvideo/*`) and a community channel (`<publisher>/*`).
4. **Reproducibility** — every install pins to a content hash in a lock file so any open-video film
   can be rebuilt from its receipt (a hard governance requirement, `GOVERNANCE.md` → Reproducibility).
5. **A marketplace** — free + premium plugins, creator profiles, download counts — that compounds the
   moat closed video platforms structurally cannot match (`docs/library-and-loras.md` §5).

### Non-goals (for v0)
- Running our own binary blob store (we use HF / Civitai / author hosts; the registry points at them).
- A payments backend in v0 (premium listing is a metadata field; checkout is Phase 3, `PLAN.md`).
- A full web IDE / visual plugin builder (use the templates in `templates/`).
- Replacing ComfyUI custom nodes — open-video **drives** ComfyUI; a plugin *may* ship ComfyUI custom
  nodes alongside its backend, but the registry is open-video's, not ComfyUI's.

---

## 1. Plugin types

The registry installs five kinds of things (the five named in the project brief). Each maps to an
existing repo directory and an existing contract — the registry does **not** invent new seams, it
automates the existing ones.

| `type` | What it is | Installs into | Contract / interface | Template |
|---|---|---|---|---|
| **`backend`** | A model plugin (H3, Wan3, FLUX3-Dev, …) | `backends/<name>/` | `ModelBackend` ABC (`core/backend.py`) — implements `prompt_guide`, `craft_prompt`, `constraints`, `generate`, `default_settings`, `duration_to_length`, `resolution_for` | `templates/model_backend.py` |
| **`engine`** | An engine adapter (ComfyUI today; diffusers/sglang later) | `engines/<name>/` | `EngineAdapter` ABC (`core/backend.py`) — implements `submit_and_wait(workflow, timeout)` | (TBD; mirror `engines/comfyui/adapter.py`) |
| **`judge`** | A judge strategy / vision-judge backend (cx+Opus pair, VideoScore, a local VLM, a best-of-N tournament) | `judges/<name>/` | a `Judge` interface returning `(verdict, issues, fix_hints)` against a quality bar (see `core/judge.py`; the interface is formalized alongside the first contributed judge) | (TBD) |
| **`lora`** | A community-trained LoRA **recipe + weights pointer** | recipe → `library/loras/<category>/`; weights → `ComfyUI/models/loras/` via `lora pull` | the LoRA recipe header (`templates/lora_recipe.md`); at runtime `ShotRequest.extra["lora"] = {"id", "strength"}` → backend injects `LoraLoader` | `templates/lora_recipe.md` |
| **`recipe`** | A library asset: prompt recipe, coherence bible, reference pack, or showcase | `library/prompts/`, `library/coherence_recipes/`, `library/reference_packs/`, `library/showcase/` | the per-kind template (`templates/prompt_recipe.md`, etc.) | per-kind |

**`recipe` subtypes** (`recipe.kind`): `prompt` | `coherence` | `reference_pack` | `showcase`. The
installer routes by `kind` to the right `library/` subdir. (A standalone `prompt` type is folded into
`recipe` to keep the type list at five and to match the `library/` directory layout — `prompts/` is a
recipe kind, not a separate extension seam.)

> **Why these five and only these:** they are exactly the extension seams already in the architecture
> (`ARCHITECTURE.md` → Layers). Adding a sixth (e.g. an `audio` post-processor) is a future RFC, not
> a v0 concern — keep the surface small so the manifest schema stays stable.

---

## 2. The `open-video install` command

A new top-level subcommand on the existing CLI (`cli/open_video.py`), sibling to `list-models`,
`list-presets`, `serve`, and the planned `lora pull`. The full subcommand family:

```
open-video install    <plugin>       install a plugin from the registry (or a local path / git URL)
open-video uninstall  <plugin>       remove a plugin + undo its install hooks
open-video update     [<plugin>]     update one plugin or all installed plugins
open-video list       [--installed|--available|--type T]   list plugins
open-video search     <query>        full-text search the registry index
open-video info       <plugin>       show the resolved manifest + install plan
open-video publish    [<path>]       package + open a registry PR (wraps §5)
open-video verify     [<plugin>]     re-run the signature + checksum + contract checks
open-video lock       [--frozen]     write/read open-video.lock
```

`open-video lora pull <id>` (from `docs/library-and-loras.md` §4) is preserved as a **back-compat
alias**: it resolves `id` to a `lora` plugin and runs `install` with `--no-deps --weights-only`.

### 2.1 Name resolution

`<plugin>` accepts the same grammar everywhere (install / info / update / uninstall / search):

| Form | Meaning | Example |
|---|---|---|
| `<name>` | Official channel — resolves to `openvideo/<name>` (mirrors Ollama's implicit `library/` namespace) | `open-video install h3` → `openvideo/h3` |
| `<publisher>/<name>` | A namespaced plugin (the canonical form; matches the LoRA `id` convention) | `open-video install acme/my_character` |
| `<publisher>/<name>@<version>` | Pinned to an exact semver | `open-video install openvideo/h3@1.2.0` |
| `<publisher>/<name>@<tag>` | A dist-tag (`latest`, `beta`, `rc`) — `latest` is the default when `@` is omitted | `open-video install openvideo/h3@beta` |
| `<publisher>/<name>:<digest>` | Content-pinned to a specific SHA256 manifest digest (Ollama-style; the most reproducible form) | `open-video install openvideo/h3:sha256-9f3c…` |
| `./path` or `../path` | A local plugin dir containing `open-video.plugin.json` (develop/test path, like `npm install ./my-pkg`) | `open-video install ./backends/my_model` |
| `<git-url>[#ref]` | A raw git URL — **only honored when `--git` (or `security.allow_git_install`) is set** (ComfyUI-Manager pattern; off by default) | `open-video install https://github.com/acme/ov-wan.git@v2` |

**Version range resolution** follows npm/semver: omit the specifier → `latest` dist-tag; `@^1.2` →
highest compatible `1.x.y ≥ 1.2.0`; `@~1.2.3` → `1.2.x`; `@>=1 <2`. Range specifiers are honored on
**transitive dependencies** (manifest `dependencies`) but the top-level `<plugin>` resolves to a
single concrete version + digest before install, and that pin is what gets written to the lock file.

### 2.2 Install lifecycle (per plugin)

For every resolved plugin the installer runs the same pipeline; only the **target** and the
**post-install hook** differ by `type`.

```
resolve(<plugin>)                         # name → (publisher, name, version, digest)
  → fetch manifest (open-video.plugin.json) from registry / local path
  → verify signature + checksum (strict/normal)            # §7
  → check host compatibility (min/max open-video, peer backends/engines)
  → resolve + install dependencies (same pipeline, recursive)
  → materialize source:
        git-clone  → shallow clone of install.source @ tag, into <target>
        tarball    → fetch + extract (checksum must match)
        hf-download→ pull weights from install.models[].repo_id (HF)
        recipe-only→ write the .md/.yaml file into <library subdir>   # no code
        weights-only→ register recipe + run `lora pull`               # LoRAs
  → run post-install hook:
        backend / engine / judge:
            - pip/uv install requirements (only if allow_pip_install) # §7
            - run the plugin's own install.py if present (opt-in, scanned)
            - import the entry class, assert it satisfies the contract
            - register alias in BACKEND_REGISTRY (or the engine/judge registry)
        lora:
            - pull weights into ComfyUI/models/loras/, verify SHA256
            - run the "trigger-fires" sanity check from the recipe before/after pair
        recipe:
            - lint the file against its template; no code exec
  → update open-video.lock (name, version, digest, source, installed_at, flags)
  → print a receipt: what was installed, from where, what it cost (GPU/disk), what it conflicts with
```

**Target directories** (computed from `type`, overridable with `--target`):

| `type` | Default target | Post-install registration |
|---|---|---|
| `backend` | `backends/<name>/` | added to `BACKEND_REGISTRY` (`cli/open_video.py`) so `--model <name>` works |
| `engine` | `engines/<name>/` | added to `ENGINE_REGISTRY` (new; mirrors `BACKEND_REGISTRY`) so `--engine <name>` works |
| `judge` | `judges/<name>/` | added to `JUDGE_REGISTRY` so `--judge <name>` works |
| `lora` | recipe → `library/loras/<category>/<publisher>__<name>.md`; weights → `ComfyUI/models/loras/<publisher>__<name>.safetensors` | referenced by `id` (publisher/name) from `ShotRequest.extra["lora"]` |
| `recipe` | `library/<{prompts,coherence_recipes,reference_packs,showcase}>/<publisher>__<name>.<ext>` | surfaced by `list-presets` / the gallery |

### 2.3 Flags

| Flag | Purpose | Default |
|---|---|---|
| `--version <spec>` / `@<spec>` | semver range or exact version | `@latest` |
| `--type {backend,engine,judge,lora,recipe}` | force a type (resolve ambiguity / install a local plugin the scanner can't classify) | inferred from manifest |
| `--git` | allow raw-git-URL install (gates `allow_git_install`) | off |
| `--pip` | allow pip/uv install of `requirements` (gates `allow_pip_install`) | off |
| `--no-deps` | skip dependency resolution | off |
| `--weights-only` | LoRA: register recipe but still pull weights; alias for `lora pull` | off |
| `--recipe-only` | LoRA/recipe: write metadata only, fetch nothing | off |
| `--target <dir>` | override the install target dir | per-type default |
| `--verify <mode>` | `strict` (require signature+checksum) \| `normal` (checksum, warn on unsigned) \| `off` | `normal` locally, `strict` on the hosted SaaS |
| `--frozen` | refuse if `open-video.lock` would change (the `npm ci` mode — for CI / SaaS reproducibility) | off |
| `--dry-run` | resolve + plan, write nothing | off |
| `--yes` | accept high-risk prompts non-interactively (still subject to security flags) | off |
| `--channel {official,community,any}` | restrict which channel to resolve from | `any` locally, `official` on SaaS |

### 2.4 The lock file — `open-video.lock`

A single repo-root JSON file pinning every installed plugin, written on every successful install and
read by every generation run. This is the **reproducibility primitive** the governance doctrine
requires (`GOVERNANCE.md` → Reproducibility: *"every generated shot records seed/model/settings; any
output can be reproduced from its receipt"*). The film's receipt references the lock file SHA so a
re-install reconstructs the exact plugin set.

```jsonc
{
  "lockfile_version": 1,
  "open_video": ">=0.1,<0.2",
  "plugins": {
    "openvideo/h3": {
      "version": "1.2.0",
      "type": "backend",
      "digest": "sha256:9f3c…",
      "source": "registry+tarball",
      "source_url": "https://github.com/open-video/registry/releases/download/openvideo__h3@1.2.0/openvideo__h3-1.2.0.tar.gz",
      "installed_at": "2026-08-03T14:21:00Z",
      "requirements_hash": "sha256:…"
    },
    "acme/my_character": {
      "version": "0.3.1",
      "type": "lora",
      "digest": "sha256:…",
      "weights": { "path": "ComfyUI/models/loras/acme__my_character.safetensors",
                   "sha256": "…", "size_mb": 180 },
      "source": "registry+recipe+hf-download"
    }
  },
  "lockfile_sha": "sha256:…"   // signs the above for tamper detection
}
```

`open-video install --frozen` (`npm ci` equivalent) fails if the manifest would resolve to a digest
not already in the lock — this is what the hosted SaaS and CI use to guarantee a film rebuilds
identically.

---

## 3. The plugin manifest — `open-video.plugin.json`

Every plugin is **one JSON manifest** plus its source (a git repo / tarball / HF path / recipe file).
The manifest is the single contract between author, registry, scanner, installer, and runtime — the
same role `package.json` plays for npm and `pyproject.toml [tool.comfy]` plays for the ComfyUI
Registry.

The manifest lives at the **root of the plugin source** (the git repo, the tarball, or alongside a
local plugin dir) and is referenced by URL from the registry index (§4).

### 3.1 Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `manifest_version` | yes | int | This schema version. Currently `1`. |
| `name` | yes | string | `<publisher>/<slug>` or `<slug>` (unscoped → official). Lowercase, ASCII, hyphens ok, no underscores in the slug beyond the LoRA convention. Max 64 chars. Must match the registry path. |
| `type` | yes | enum | `backend` \| `engine` \| `judge` \| `lora` \| `recipe`. |
| `version` | yes | semver | The plugin's version. **Published versions are immutable** (ComfyUI Registry rule): to change code, publish a new version; deprecated versions stay resolvable but flagged. |
| `description` | yes | string | One line. Surfaced in `search`, `info`, and the marketplace. |
| `author` | yes | object \| string | `{name, email?, url?}` — the publisher identity. Must match the `name`'s `<publisher>` for community plugins. |
| `license` | yes | SPDX | e.g. `Apache-2.0`, `MIT`, `CC-BY-4.0`. LoRAs: must match the weights' actual license (`docs/library-and-loras.md` §7). |
| `license_restricted` | lora/recipe | bool | `true` if commercial/exclusive-restricted. Excludes from the "remix freely" gallery filter. |
| `homepage` | – | url | Project page. |
| `repository` | – | url | Source code. |
| `bugs` | – | url \| object | Issue tracker. |
| `keywords` / `tags` | – | string[] | Search/discovery; for LoRAs `category` is the primary tag. |
| `category` | lora | enum | `cinematic` \| `anime` \| `product` \| `character` \| `style` (from `docs/library-and-loras.md` §2). |
| `kind` | recipe | enum | `prompt` \| `coherence` \| `reference_pack` \| `showcase`. |
| `install` | yes | object | **How to materialize the plugin.** See 3.2. |
| `entry` | code types | string | The file that implements the contract, relative to source root: `backend.py` / `adapter.py` / `judge.py`. |
| `class` | code types | string | The class to instantiate (`YourModelBackend`). The installer imports it and asserts it subclasses the right ABC. |
| `capabilities` | backend/judge | object | A summary of `Capabilities` (t2v/i2v/flf2v/r2v/native_audio/max_duration_s/strengths) for `list-models` and the selector *before* the plugin is imported — so routing doesn't require loading the backend. |
| `dependencies` | – | object | `{ "openvideo/wan2": "^1.0", "acme/grade": "^0.2" }` — other open-video plugins, semver ranges. Resolved recursively. |
| `requirements` | code types | string[] | pip/uv Python deps. **Only installed when `allow_pip_install` is set** (§7). Each entry is a single line; `requirements.txt` files in the source are honored the same way. |
| `comfyui_nodes` | – | object | Optional ComfyUI custom nodes shipped alongside (for a backend that needs custom nodes in the workflow). Listed as `{repo, commit?, subdir?}`; installed into `ComfyUI/custom_nodes/` only when `--git` is set. The scanner treats these the same as any code (§7). |
| `models` | backend/lora | object[] | Weight references: `{name, repo_id, path_in_repo, sha256, size_mb, format}`. `format` must be `safetensors` in `strict`/`normal` (§7). This is the Ollama-blob equivalent — content-addressed, resumable. |
| `base_model` | lora | string | The backbone the LoRA was trained against (e.g. `MiniMax H3 (int8 ConvRot, Comfy-Org)`). Mirrors Ollama `FROM`. The installer warns if the resolved engine/backend doesn't match. |
| `min_open_video` / `max_open_video` | – | semver | Host compatibility (npm `engines`). The installer refuses if open-video is outside the range, unless `--force`. |
| `peers` | – | object | `{ "engine": "comfyui@^1", "backend": "openvideo/h3@^1" }` — like `peerDependencies`: this plugin needs a compatible engine/backend present. Warned, not auto-installed, unless listed in `dependencies`. |
| `checksum` | yes on publish | string | `sha256:<hex>` of the source tarball (computed by the registry on publish; authors don't set it by hand). |
| `signature` | – | object | Optional sigstore/cosign signature over `checksum`. Required for `verified` status in the official channel. |
| `premium` | – | object | Marketplace: `{price_usd, currency, take_rate?}`. See §6. |
| `gallery` | lora/recipe | object | `{before_url, after_url, thumbnail_url}` — the before/after pair that proves the asset works (`docs/library-and-loras.md` §3, §7). Required for LoRAs to pass review. |
| `verified` | – (registry-set) | bool | Set by the registry after scan + review (§5, §7). **Not author-set.** |
| `deprecated` | – (registry-set) | bool \| string | Set by the registry for takedown; string carries the deprecation reason + successor. |

### 3.2 The `install` object

`install.method` selects the materializer; the rest of the object feeds it.

| `method` | Used by | Required keys | Behavior |
|---|---|---|---|
| `git-clone` | backend / engine / judge | `source` (git URL), `ref` (tag/commit/branch) | Shallow clone into `<target>`. Pinned to `ref`; the commit SHA is recorded as the digest. |
| `tarball` | backend / engine / judge | `source` (https URL), `checksum` (sha256) | Fetch + verify checksum + extract into `<target>`. Preferred for reproducibility (content-addressed). |
| `hf-download` | backend / lora (weights) | `models[]` (each with `repo_id`, `path_in_repo`, `sha256`) | Pull weights from Hugging Face into `ComfyUI/models/<kind>/`. SHA256 verified per blob (Ollama-pull semantics; resumable). |
| `weights-only` | lora | `recipe_path`, `models[]` | Register the LoRA recipe in `library/loras/<category>/` **and** pull weights (this is what `lora pull <id>` does). |
| `recipe-only` | recipe, or LoRA-without-weights | `recipe_path` (path inside source to the `.md`/`.yaml`) | Copy the file into the right `library/` subdir. No code, no weights. |

`recipe_path` is the path *inside the plugin source* to the recipe/asset file; the installer copies it
to `library/.../<publisher>__<name>.<ext>`.

### 3.3 Examples (one per type)

**Backend** (`openvideo/h3`):
```jsonc
{
  "manifest_version": 1,
  "name": "openvideo/h3",
  "type": "backend",
  "version": "1.2.0",
  "description": "MiniMax H3 backend — 3-field grammar, FL2VA/T2V/R2V, native audio, 4–15s.",
  "author": { "name": "openvideo", "url": "https://open-video.ai" },
  "license": "Apache-2.0",
  "install": { "method": "tarball",
    "source": "https://github.com/open-video/registry/releases/download/openvideo__h3@1.2.0/openvideo__h3-1.2.0.tar.gz",
    "checksum": "sha256:9f3c…" },
  "entry": "backend.py",
  "class": "H3Backend",
  "capabilities": { "t2v": true, "i2v": true, "flf2v": true, "r2v": true,
                    "native_audio": true, "max_duration_s": 15,
                    "strengths": ["audio", "prompt-adherence"] },
  "models": [
    { "name": "h3-int8-convrot", "repo_id": "Comfy-Org/HunyuanVideo-Artelake",
      "path_in_repo": "…/h3_int8_convrot.safetensors", "format": "safetensors",
      "sha256": "…", "size_mb": 18000 }
  ],
  "peers": { "engine": "comfyui@^1" },
  "min_open_video": "0.1.0",
  "verified": true
}
```

**Engine** (`openvideo/comfyui`):
```jsonc
{
  "manifest_version": 1, "name": "openvideo/comfyui", "type": "engine", "version": "1.0.0",
  "description": "ComfyUI HTTP API engine adapter — submit/wait/fetch workflows.",
  "author": { "name": "openvideo" }, "license": "Apache-2.0",
  "install": { "method": "tarball", "source": "…/openvideo__comfyui-1.0.0.tar.gz", "checksum": "sha256:…" },
  "entry": "adapter.py", "class": "ComfyUIAdapter",
  "min_open_video": "0.1.0", "verified": true
}
```

**Judge** (`acme/cx-opus-pair`):
```jsonc
{
  "manifest_version": 1, "name": "acme/cx-opus-pair", "type": "judge", "version": "0.2.0",
  "description": "Two-vision-critic judge: cx (GPT-5.6) + Opus 4.8 must both pass (cross-model-review).",
  "author": { "name": "acme" }, "license": "Apache-2.0",
  "install": { "method": "git-clone", "source": "https://github.com/acme/ov-cx-opus-pair.git", "ref": "v0.2.0" },
  "entry": "judge.py", "class": "CxOpusPairJudge",
  "capabilities": { "vision": true, "best_of_n": true, "needs_api_keys": ["CX_API_KEY", "OPUS_API_KEY"] },
  "requirements": ["openai>=1.0", "anthropic>=0.40"],
  "verified": false
}
```

**LoRA** (`acme/my_character`):
```jsonc
{
  "manifest_version": 1, "name": "acme/my_character", "type": "lora", "version": "0.3.1",
  "description": "Character LoRA: the lighthouse keeper — locks face + wardrobe across re-rolls.",
  "author": { "name": "acme" }, "license": "Apache-2.0", "license_restricted": false,
  "category": "character", "tags": ["cinematic", "hero-shot"],
  "base_model": "MiniMax H3 (int8 ConvRot, Comfy-Org)",
  "install": { "method": "weights-only", "recipe_path": "my_character.recipe.md",
    "models": [
      { "name": "my_character", "repo_id": "acme/h3-loras", "path_in_repo": "my_character.safetensors",
        "format": "safetensors", "sha256": "…", "size_mb": 180 } ] },
  "gallery": { "before_url": "https://…/before.mp4", "after_url": "https://…/after.mp4",
               "thumbnail_url": "https://…/thumb.jpg" },
  "verified": false
}
```

**Recipe** (`openvideo/trailer-coherence`):
```jsonc
{
  "manifest_version": 1, "name": "openvideo/trailer-coherence", "type": "recipe", "version": "1.0.0",
  "kind": "coherence",
  "description": "Pre-built coherence bible for a 60s trailer (acts, transitions, state vectors).",
  "author": { "name": "openvideo" }, "license": "CC-BY-4.0",
  "install": { "method": "recipe-only", "recipe_path": "trailer.yaml" },
  "min_open_video": "0.1.0", "verified": true
}
```

The full JSON Schema (for validation) is in Appendix A.

---

## 4. The registry index

The registry is the community-curated list that name resolution queries. It is **two things**:

1. A **GitHub repo** — `github.com/open-video/registry` — the source of truth, updated by PR (the
   ComfyUI-Manager `custom-node-list.json` model). Every change is reviewable + revertible.
2. A **read-only HTTP mirror** at `https://open-video.ai/registry` (and `https://open-video.ai/registry/index.json`)
   — what the CLI fetches. It is regenerated from the GitHub repo by CI on every merge, served via
   GitHub Pages or a thin CDN, and **signed** (sigstore bundle) so a compromised mirror can't slip a
   malicious index past `--verify strict`.

### 4.1 Channels

Two tiers, mirroring Ollama's official-vs-namespace split and npm's scoped-public model:

| Channel | Path in repo | `verified` gate | Trust level |
|---|---|---|---|
| **official** (`openvideo/*`) | `plugins/openvideo/<name>.json` (+ versions under `plugins/openvideo/<name>/<version>.json`) | Required: scan + human two-eyes review + signature | Default for the hosted SaaS; what `install <name>` (unscoped) resolves to |
| **community** (`<publisher>/*`) | `plugins/<publisher>/<name>.json` | Scan always; human review on first publish of a publisher, then trust-ratchet (§5) | Default for local; what `install <publisher>/<name>` resolves to |

A plugin **cannot** move between channels: a community plugin does not get re-published as official by
renaming; "official" requires the open-video council's adoption (RFC, like ComfyUI's verification).

### 4.2 Index format — `registry/index.json`

The top-level index the CLI fetches. It is **derived** (by a `scanner.py` equivalent in CI) from the
per-plugin manifests — authors edit manifests, CI rebuilds the index. Mirrors ComfyUI-Manager's
`extension-node-map.json` + `github-stats.json` derivation.

```jsonc
{
  "index_version": 1,
  "generated_at": "2026-08-03T14:00:00Z",
  "signature": { "kind": "sigstore", "bundle_url": "…/index.json.sigstore" },
  "plugins": [
    {
      "name": "openvideo/h3", "type": "backend", "version": "1.2.0",
      "latest": "1.2.0", "tags": { "latest": "1.2.0", "beta": "1.3.0-beta.2" },
      "description": "MiniMax H3 backend …",
      "author": "openvideo", "license": "Apache-2.0", "verified": true,
      "category": null, "channel": "official",
      "manifest_url": "https://open-video.ai/registry/plugins/openvideo/h3/1.2.0.json",
      "digest": "sha256:9f3c…",
      "stats": { "downloads_30d": 18420, "stars": 312, "installed_total": 9011,
                 "updated_at": "2026-07-29T…" },
      "capabilities": { "t2v": true, "i2v": true, "flf2v": true, "r2v": true,
                        "native_audio": true, "max_duration_s": 15 },
      "gallery": null,
      "premium": null,
      "deprecated": false
    }
    // …one entry per (publisher, name), pointing at the latest version's manifest
  ],
  "versions": {
    // optional: per-plugin version→digest map for range resolution, paginated on the HTTP API
    "openvideo/h3": { "1.2.0": "sha256:9f3c…", "1.1.0": "sha256:…", "1.3.0-beta.2": "sha256:…" }
  }
}
```

The HTTP API also exposes per-plugin endpoints mirroring npm's `/<@scope>/<name>` route:

- `GET /registry/plugins/<publisher>/<name>.json` — latest version manifest + version list (npm-style
  packument).
- `GET /registry/plugins/<publisher>/<name>/<version>.json` — exact version manifest (immutable).
- `GET /registry/plugins/<publisher>/<name>/<version>.tar.gz` — the tarball (immutable).
- `GET /registry/search?q=<query>&type=<t>&channel=<c>` — search the index.
- `GET /registry/stats/<publisher>/<name>.json` — download/usage stats.

### 4.3 Resolution flow (what `open-video install` does against the index)

```
1. GET /registry/index.json  → verify signature (strict/normal) → cache locally (15 min)
2. resolve <plugin> name → entry (or error: not found / not in allowed channel)
3. resolve version: latest-tag | range | exact | digest  → concrete (version, manifest_url, digest)
4. GET manifest_url          → the open-video.plugin.json for that version
5. verify manifest digest == index digest (immutability check; mismatch = registry corruption)
6. run §2.2 install lifecycle
```

The index is fetched once and cached; subsequent installs in the same session don't re-fetch.
`open-video install --refresh` forces a re-fetch.

### 4.4 Content addressing for weights (the Ollama layer)

LoRA / backend weights are content-addressed by SHA256 in `models[].sha256`. The installer:

1. Streams the blob (HF/Civitai/author host) to a `.partial` file, **resumable** (Ollama pull
   semantics — a cancelled install resumes from the byte offset).
2. Verifies `sha256(blob) == manifest.models[].sha256` before moving it into place.
3. Stores under a content-addressed cache (`~/.cache/open-video/blobs/sha256/<digest>`) and
   hardlinks/symlinks into `ComfyUI/models/<kind>/<publisher>__<name>.<ext>`. Two plugins referencing
   the same backbone weights share one blob on disk (Ollama layer reuse).

This is why a LoRA manifest can be `:sha256-…`-pinned: the digest pins the *weights*, not just the
recipe — the most reproducible form, and the one the hosted SaaS uses.

---

## 5. Publishing a plugin

The publish flow is a thin wrapper around "open a PR to `open-video/registry`," modeled on
`comfyregistry publish` and `npm publish` but with a mandatory automated scan + a trust ratchet.

### 5.1 Author

1. **Scaffold from a template.** `backend`/`engine`/`judge`: `cp -r templates/model_backend.py …`
   (or the engine/judge template) into a new dir. `lora`/`recipe`: copy the recipe template
   (`templates/lora_recipe.md` / `templates/prompt_recipe.md`).
2. **Write `open-video.plugin.json`** at the source root (§3). For code plugins, set `entry` + `class`
   + `capabilities`; for LoRAs set `category` + `gallery` (the before/after pair); for recipes set
   `kind` + `install.recipe_path`.
3. **Test locally.** `open-video install ./my-plugin --target backends/my_model --type backend`.
   The installer loads the plugin from a path (no registry round-trip), runs the contract check,
   and lets you `open-video "…" --model my_model --dry-run` to confirm it integrates.
4. **Run the scanner yourself.** `open-video verify ./my-plugin` runs the same checks the registry CI
   will (§7) so you don't get bounced at PR.

### 5.2 Publish

`open-video publish [<path>]` wraps the registry-PR mechanics (it forks/clones `open-video/registry`,
writes your manifest under `plugins/<publisher>/<name>/<version>.json`, uploads the tarball as a
GitHub release asset, and opens a PR):

```
open-video publish ./backends/my_model
# → builds tarball, computes checksum, signs (if a signing key is configured)
# → opens PR: "registry: add acme/my_model@0.1.0"
```

You can also do it by hand: fork `open-video/registry`, add the manifest + tarball, open a PR. The CLI
just removes the toil.

### 5.3 Review gates (automated then human)

Registry CI runs on every PR (this is the ComfyUI scanner + npm publish-gate, combined):

**Automated (always, blocks merge):**
- **Manifest lint** — schema validity, name/version/license/author sanity, `name` matches PR path.
- **Contract conformance** — for code plugins, import `entry.class` and assert it subclasses the right
  ABC (`ModelBackend` / `EngineAdapter` / `Judge`) and that `capabilities` matches the class's actual
  `Capabilities`.
- **Scanner** (ComfyUI-Manager's malicious-behavior model) — flags, for the diff's code:
  - custom pip wheels (`.whl` files in the source or pulled by `install.py`),
  - `subprocess`/`os.system`/`shell=True` calls whose target is outside the engine/generation path
    (arbitrary system calls),
  - network egress from an `install.py` that isn't fetching declared `models[]`,
  - `pickle` / `torch.load` on untrusted input (pickle RCE vector — why strict/normal require
    `safetensors`),
  - credential/file-system reads outside the plugin's target dir during install.
- **Dependency audit** — `pip-audit` over `requirements`; known CVEs block, advisories warn.
- **Plugin tests** — run the plugin's own test suite if it declares one.
- **License + consent** (LoRA/recipe) — trigger word present in `gallery.after_url`'s prompt, the
  before/after pair is *visibly* different (the `docs/library-and-loras.md` §7 "does what it claims"
  check), `license_restricted` set honestly.

**Human review (first publish of a `publisher`, or any `official` channel request):**
- Two-eyes from the review council on the code/recipe. Check: does the claimed capability match
  reality? Is the before/after honest? Is consent provenance clean? This is the LoRA review bar from
  `docs/library-and-loras.md` §7, generalized to all plugin types.

**The trust ratchet (after first publish):**
- Once a publisher has one human-reviewed plugin, **subsequent versions** of that *same* plugin ship
  on scan-only (no fresh human review) — the npm trusted-publisher model. A new plugin *from the same
  publisher* still gets one human review. Abuse of the ratchet (a scanned-only version ships
  malicious code that the scanner missed) triggers publisher suspension + takedown (§7).

### 5.4 Merge → list

On merge, CI:
1. Tags `plugins/<publisher>/<name>/<version>.json` as immutable.
2. Rebuilds `index.json` from all manifests (scanner.py derivation), recomputes stats.
3. Re-signs the index (sigstore).
4. Sets `verified` per the channel rules (official always; community after the ratchet).
5. Publishes the new index to `open-video.ai/registry`.

A merged version is **immutable**: to fix a bug, publish `0.1.1`. To retract, the council sets
`deprecated: <reason>` (ComfyUI's "deprecate a version") — the version stays resolvable but the
installer warns and refuses unless `--include-deprecated`.

---

## 6. The marketplace vision

The registry is the substrate; the marketplace is the product surface on top. It turns the library
flywheel (`docs/library-and-loras.md` §5) into a creator economy — and it's the Phase 3 revenue
surface (`PLAN.md`).

### 6.1 Free + premium

| Tier | License | Listing | Discovery |
|---|---|---|---|
| **Free (open)** | Apache-2.0 / MIT / CC-BY | Always free; `premium: null` | Default gallery + search |
| **Free (restricted)** | CC-BY-NC / commercial-restricted | `license_restricted: true`, `premium: null` | Excluded from "remix freely"; shown with a license badge |
| **Premium** | creator-set | `premium: { price_usd, currency }` | Shown with price; install requires a purchase/license token |

Premium metadata is just a field in the manifest — the registry stores it; checkout is Phase 3 (target
Stripe Connect for creator payouts). A premium plugin's tarball is gated by a license token at the
HTTP layer; the manifest stays public so discovery works.

### 6.2 Creator profiles

A `publisher` namespace **is** a profile page at `open-video.ai/<publisher>`:
- Display name, bio, links, "verified creator" badge (issued by the council — distinct from per-plugin
  `verified`).
- All their plugins (free + premium), aggregate download counts, follower count.
- A `/registry/<publisher>.json` API for programmatic access.

This is the npm-maintainer + Civitai-creator pattern. The publisher of record is set at first publish
and bound to a GitHub identity; transfers require council sign-off (anti-squatter / anti-hijack).

### 6.3 Download counts + stats

`stats` in the index (§4.2) is fed by the HTTP mirror logging install events (anonymized:
plugin + version + timestamp + channel, no user data). Surfaced on:
- the marketplace listing (30-day + total downloads),
- creator profiles (aggregate),
- a public leaderboard (`open-video.ai/leaderboard`) — the seed of the "best community LoRAs" social
  signal that closed platforms can't replicate.

### 6.4 The take rate (Phase 3, owner-decided)

The lean target is a single-digit-to-low-teens take rate on premium plugins (the owner decides the
exact number; this spec only fixes the *field*). The creator sets the price; open-video routes
payment; the registry records the license token. This is deliberately out of scope for v0 — the
manifest just carries `premium` so the schema doesn't change when checkout lands.

### 6.5 Why this compounds (the moat, restated)

Closed video platforms ship **one** model and forbid community models outright
(`docs/library-and-loras.md` §5). A registry + marketplace makes the open side a **long-tail
economy**: every aesthetic, every character lock, every product SKU, every niche motion style becomes
a plugin someone can ship and price. The marketplace doesn't create the moat — the *community library*
does (`docs/library-and-loras.md`) — but it gives contributors a profile, a download count, and
(eventually) revenue, which is what turns a one-off LoRA into a sustained creator habit. That habit is
the thing closed platforms can't match.

---

## 7. Security

Installing and running third-party code is the highest-risk surface in the project. The model is
ComfyUI-Manager's tiered `security_level` + decoupled allow-flags, plus Ollama-style content
addressing for weights, plus a scanner gate at publish.

### 7.1 Tiered security model

A single setting — `security.level` in `~/.config/open-video/config.toml` or `--verify <mode>` —
gates install behavior. Three levels (ComfyUI-Manager has four; we collapse `normal-` into `normal`):

| | **strict** (hosted SaaS default) | **normal** (local default) | **yolo** (opt-in, your machine) |
|---|---|---|---|
| Resolve from | **official channel only** | official + community | any, incl. raw git URLs |
| Signature on index/manifest | **required** | verified if present, warn if absent | ignored |
| Checksum on tarball/weights | required | required | optional |
| Weights format | `safetensors` only | `safetensors` only | any (incl. pickle) — at your risk |
| `allow_pip_install` | **false** (code plugins ship pre-baked, or fail) | opt-in flag | opt-in flag |
| `allow_git_install` | **false** | opt-in flag | opt-in flag |
| Run `install.py` hooks | **false** | opt-in flag | opt-in flag |
| Unverified community code plugin | refused | allowed with a loud warning | allowed silently |
| Frozen lock (`--frozen`) | enforced (SaaS + CI) | optional | optional |

The hosted SaaS runs `strict` always — a hosted user never executes unaudited third-party code on
open-video's GPUs. Local users default to `normal` (you installed it, you accept it) and can ratchet
to `yolo` for development.

### 7.2 Decoupled allow-flags (the ComfyUI-Manager rule, kept exactly)

`allow_git_install`, `allow_pip_install`, `allow_install_hooks` are **fully decoupled** from
`security.level` — they default to `false`, they take effect **only when the process is on a loopback
address** (i.e. a local install, not driven by a remote HTTP request), and they must be turned on
explicitly. This is the exact ComfyUI-Manager invariant; it prevents a remote attacker who can reach
the open-video HTTP API from forcing a `pip install` of an attacker-controlled wheel.

### 7.3 Sandboxing

- **v0 (honest):** code plugins (`backend`/`engine`/`judge`) run **in-process**, like ComfyUI custom
  nodes. This is an accepted, documented risk: a malicious verified plugin can do anything the
  open-video process can. Mitigations: the scanner gate (§7.4) + the review ratchet (§5.3) + the
  `strict` channel on the SaaS. We do not pretend in-process is sandboxed.
- **Path confinement:** even in-process, the installer's post-install hook and the plugin's
  `install.py` run under a path guard that **rejects writes outside** the plugin's target dir, the
  `ComfyUI/models/` tree, and the open-video cache. Network calls during install are restricted to
  the declared `models[]` hosts.
- **v1 (target):** an optional `--sandbox` mode that runs unverified code plugins in a subprocess
  with a seccomp/AppArmor profile (or a container), communicating over a thin RPC. The `Judge` and
  `EngineAdapter` seams are RPC-friendly by construction (one method in, one result out); backends
  are harder (they own the workflow dict) and may stay in-process even in `--sandbox` mode. This is a
  future RFC, not a v0 deliverable.

### 7.4 The scanner (publish-time + local `verify`)

The same scanner runs in registry CI (§5.3) and in `open-video verify`. It is rule-based, not a magic
AI judge, and its findings are the gate for `verified` status:

| Rule | Severity | Action |
|---|---|---|
| `.whl` / `.tar.gz` Python packages in source or fetched by `install.py` | block | custom pip wheels are the classic supply-chain vector; refuse |
| `pickle.load` / `torch.load(..., weights_only=False)` on non-constant input | block | pickle RCE |
| Weights not `safetensors` (strict/normal) | block | pickling attack surface |
| `subprocess`/`os.system`/`shell=True` to targets outside the engine/generation path | block (review) | arbitrary system calls |
| Network egress in `install.py` not matching `models[]` hosts | block | exfil |
| Reads of `~/.ssh`, `~/.aws`, env of unrelated tools, browser profiles | block | credential theft |
| Missing `license` / `author` / `gallery` (LoRA) / consent fields | block | metadata integrity |
| `pip-audit` CVEs in `requirements` | block (critical) / warn | supply chain |

A scanner pass is **necessary** for `verified`; it is not **sufficient** for the official channel
(human review still required, §5.3). The scanner ruleset is versioned in the registry repo and
itself PR-reviewed — the gate is public, not magic.

### 7.5 Takedown

- **Deprecate a version** — the council sets `deprecated: <reason>` on a version (ComfyUI's model).
  It stays resolvable; the installer warns and refuses unless `--include-deprecated`.
- **Pull a version** — for actively-malicious content, the version is removed from the index and a
  security advisory is filed (GitHub Security Advisories, CVE-style). The tarball digest is added to
  a revocation list the installer checks at resolve time, so even a cached copy is refused.
- **Suspend a publisher** — repeated malicious publishes, or abuse of the trust ratchet, suspends the
  publisher namespace pending council review. Existing installs keep working (the lock file pins
  them); new installs are refused.

---

## 8. Cross-cutting: how this fits with what exists

### 8.1 Compatibility with the existing LoRA / recipe flow

`docs/library-and-loras.md` already defines the LoRA recipe format, the `lora pull <id>` helper, and
the PR-into-`library/` flow for recipes. The registry **absorbs** these without breaking them:

- A LoRA recipe that today is PR'd into `library/loras/` is, in registry terms, a `type: "lora"`
  plugin with `install.method: "weights-only"`. The recipe file becomes `install.recipe_path`.
- `open-video lora pull <id>` is a back-compat alias for `open-video install <id> --weights-only`.
- Recipes that ship in-repo (`library/prompts/`, etc.) keep working; the registry is an *additional*
  install path, not a replacement. `list-presets` lists both installed-by-registry and in-repo recipes.

The official open-video `library/` is, in effect, the seed content for `openvideo/*` recipes.

### 8.2 Compatibility with `BACKEND_REGISTRY` and discovery

`cli/open_video.py` already has an explicit `BACKEND_REGISTRY` + directory-walking discovery. The
installer integrates by:
- writing newly-installed backends into `backends/<name>/backend.py` (where discovery already looks),
  and appending the alias to a generated `installed_plugins.py` that `BACKEND_REGISTRY` merges in.
- The same pattern adds `ENGINE_REGISTRY` and `JUDGE_REGISTRY` (new, small).

So `list-models` continues to work unchanged; installed plugins simply appear in it.

### 8.3 Reproducibility (governance hook)

`GOVERNANCE.md` → Reproducibility requires that every shot records `seed/model/settings/prompt` and
that any output can be reproduced from its receipt. The lock file (§2.4) closes the last gap: the
**plugin set** is now pinned too. A film receipt will reference `open-video.lock` SHA, so a re-install
(`open-video install --frozen`) reconstructs identical backends/judges/LoRAs. This is the
`npm ci`-for-video invariant.

### 8.4 Honest status (2026-08)

- **Spec only.** No installer client, registry repo, index, scanner, or signed mirror exists yet.
- The seams the registry automates (`ModelBackend`, `EngineAdapter`, the LoRA recipe contract) **do**
  exist and are exercised by H3 + ComfyUI.
- Implementation phases (proposed, to be scheduled against `PLAN.md`):
  - **Phase 1** — registry repo + `open-video install` for `recipe` + `lora` (metadata/weights only,
    lowest risk, immediate value for the library flywheel); official channel seeded from `library/`.
  - **Phase 1.5** — `backend` / `engine` install (git-clone + tarball); `BACKEND_REGISTRY` merge;
    `open-video.lock`; `--frozen` for CI.
  - **Phase 2** — `judge` type; scanner in CI; community channel + trust ratchet; signed index.
  - **Phase 3** — marketplace: creator profiles, download stats public, `premium` + checkout.

---

## Appendix A — JSON Schema for `open-video.plugin.json`

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://open-video.ai/registry/schema/plugin-v1.json",
  "type": "object",
  "required": ["manifest_version", "name", "type", "version", "description", "author", "license", "install"],
  "additionalProperties": false,
  "properties": {
    "manifest_version": { "const": 1 },
    "name": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,30}(/[a-z0-9_][a-z0-9_-]{0,62})?$", "maxLength": 96 },
    "type": { "enum": ["backend", "engine", "judge", "lora", "recipe"] },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+(-[0-9A-Za-z.-]+)?(\\+[0-9A-Za-z.-]+)?$" },
    "description": { "type": "string", "maxLength": 200 },
    "author": { "oneOf": [
      { "type": "string" },
      { "type": "object", "required": ["name"], "properties": {
          "name": { "type": "string" }, "email": { "type": "string", "format": "email" },
          "url": { "type": "string", "format": "uri" } } } ] },
    "license": { "type": "string" },
    "license_restricted": { "type": "boolean" },
    "homepage": { "type": "string", "format": "uri" },
    "repository": { "type": "string", "format": "uri" },
    "bugs": { "oneOf": [ { "type": "string", "format": "uri" }, { "type": "object" } ] },
    "keywords": { "type": "array", "items": { "type": "string" } },
    "tags": { "type": "array", "items": { "type": "string" } },
    "category": { "enum": ["cinematic", "anime", "product", "character", "style"] },
    "kind": { "enum": ["prompt", "coherence", "reference_pack", "showcase"] },
    "install": {
      "type": "object", "required": ["method"],
      "properties": {
        "method": { "enum": ["git-clone", "tarball", "hf-download", "weights-only", "recipe-only"] },
        "source": { "type": "string" }, "ref": { "type": "string" },
        "checksum": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
        "recipe_path": { "type": "string" },
        "models": { "type": "array", "items": { "$ref": "#/$defs/modelRef" } }
      }
    },
    "entry": { "type": "string" },
    "class": { "type": "string" },
    "capabilities": { "type": "object" },
    "dependencies": { "type": "object", "additionalProperties": { "type": "string" } },
    "requirements": { "type": "array", "items": { "type": "string" } },
    "comfyui_nodes": { "type": "array", "items": { "type": "object" } },
    "models": { "type": "array", "items": { "$ref": "#/$defs/modelRef" } },
    "base_model": { "type": "string" },
    "min_open_video": { "type": "string" }, "max_open_video": { "type": "string" },
    "peers": { "type": "object", "additionalProperties": { "type": "string" } },
    "checksum": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
    "signature": { "type": "object" },
    "premium": { "type": "object", "properties": {
        "price_usd": { "type": "number", "minimum": 0 },
        "currency": { "type": "string", "default": "USD" } } },
    "gallery": { "type": "object", "properties": {
        "before_url": { "type": "string", "format": "uri" },
        "after_url": { "type": "string", "format": "uri" },
        "thumbnail_url": { "type": "string", "format": "uri" } } },
    "verified": { "type": "boolean" },
    "deprecated": { "oneOf": [ { "type": "boolean" }, { "type": "string" } ] }
  },
  "$defs": {
    "modelRef": {
      "type": "object", "required": ["name", "repo_id", "path_in_repo", "format", "sha256"],
      "properties": {
        "name": { "type": "string" }, "repo_id": { "type": "string" },
        "path_in_repo": { "type": "string" },
        "format": { "enum": ["safetensors", "gguf", "pt", "other"] },
        "sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
        "size_mb": { "type": "number" }
      }
    }
  }
}
```

Note: `verified` and `deprecated` are **registry-set** fields; the schema allows them but authors
must not set `verified` (CI strips/overwrites it on publish).

---

## Appendix B — CLI quick reference

```
# Install
open-video install h3                      # official channel, @latest
open-video install openvideo/h3@^1.2       # semver range
open-video install acme/my_character       # community LoRA (recipe + weights)
open-video install acme/grade@beta         # dist-tag
open-video install openvideo/h3:sha256-9f3c…   # content-pinned (most reproducible)
open-video install ./backends/my_model --type backend   # local dev

# Manage
open-video list --installed                # what's on this machine
open-video list --available --type lora    # browse the registry
open-video search "anime style"            # full-text
open-video info acme/my_character          # resolved manifest + install plan
open-video update                          # update everything (respecting ranges)
open-video uninstall acme/my_character     # remove + undo hooks

# Reproducibility
open-video lock                            # write open-video.lock
open-video install --frozen                # npm-ci mode: refuse drift
open-video install --refresh               # re-fetch the index

# Publish
open-video verify ./my-plugin              # run the scanner locally
open-video publish ./my-plugin             # package + open registry PR

# Back-compat
open-video lora pull acme/my_character     # == install acme/my_character --weights-only
```

---

## Appendix C — Reference patterns (provenance)

- **ComfyUI Manager** (`github.com/ltdrdata/ComfyUI-Manager`): `custom-node-list.json` PR-curated
  registry; `scanner.py`/`scan.sh` derives `extension-node-map.json` + `github-stats.json`; tiered
  `security_level` (strong/normal/normal-/weak); decoupled `allow_git_url_install` / `allow_pip_install`
  flags that only apply on loopback; V3.38 manager data moved to protected `<USER>/__manager/`.
- **ComfyUI Registry** (`registry.comfy.org`, `docs.comfy.org/registry/overview`): globally-unique
  node names; semver; **immutable published versions** ("once published, cannot be changed");
  "deprecate a version" takedown; scanner flags custom pip wheels + arbitrary system calls; verified
  flag in UI; `[tool.comfy]` in `pyproject.toml` as the publisher/name spec.
- **npm** (`docs.npmjs.com/cli/v10/configuring-npm/package-json`): `name`/`version`/`description`/
  `author`/`license`/`homepage`/`bugs`/`keywords` field vocabulary; scoped `@scope/name`; semver
  ranges (`^`/`~`/`>=`/`*`); `latest` dist-tag; `peerDependencies` (host compat) + `engines` (runtime
  compat); registry resolution via packument `/<@scope>/<name>`; `npm ci` frozen installs; per-package
  download counts.
- **Ollama** (`github.com/ollama/ollama` API + model docs): `namespace/model:tag` with implicit
  `library/` official namespace; `FROM <base>` layering; SHA256 content-addressed blobs + manifests;
  resumable pulls; derived models reuse base layers; `parent_model` lineage.
