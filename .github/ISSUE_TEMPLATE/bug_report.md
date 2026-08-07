---
name: Bug Report
description: Report a bug in OpenVideo (CLI, installer, H3 backend, pipeline)
title: "[bug] "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting. Please include enough detail to reproduce without your private GPU logs if possible.
  - type: textarea
    id: describe
    attributes:
      label: Describe the bug
      description: What went wrong?
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: To reproduce
      description: Exact commands (redact secrets).
      placeholder: |
        open-video pull h3 --check-only
        open-video run "…" --duration 5
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: OpenVideo version / commit
      placeholder: "0.1.0a1 or git rev-parse --short HEAD"
  - type: input
    id: os
    attributes:
      label: OS
      placeholder: Ubuntu 22.04 / macOS / Windows+WSL2
  - type: input
    id: gpu
    attributes:
      label: GPU + VRAM
      placeholder: RTX 5090 32GB / none (dry-run only)
  - type: dropdown
    id: area
    attributes:
      label: Area
      options:
        - CLI
        - Installer
        - H3 / ComfyUI
        - Pipeline / stitch
        - Judge
        - Docs
        - Other
  - type: textarea
    id: logs
    attributes:
      label: Logs / output
      render: shell
