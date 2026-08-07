---
name: Feature Request
description: Propose a feature, model backend, or library contribution path
title: "[feat] "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem / motivation
      description: What user need does this address?
    validations:
      required: true
  - type: textarea
    id: proposal
    attributes:
      label: Proposed solution
      description: How should it work? Plugin point if known (backend / judge / engine / library).
    validations:
      required: true
  - type: dropdown
    id: surface
    attributes:
      label: Contribution surface
      options:
        - Model backend (backends/)
        - Judge plugin (judges/)
        - Engine adapter (engines/)
        - Prompt / recipe (library/)
        - CLI / install
        - Docs
        - Other
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives considered
  - type: checkboxes
    id: willing
    attributes:
      label: Contribution
      options:
        - label: I am willing to open a PR for this
        - label: This is a request only
