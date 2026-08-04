---
name: Research question
description: Ask a question about the EADS research design, module-to-paper mapping, or reproducibility.
title: "[Research] "
labels: ["question", "research"]
body:
  - type: textarea
    id: question
    attributes:
      label: Question
      description: What would you like to clarify?
    validations:
      required: true
  - type: input
    id: paper
    attributes:
      label: Paper or module
      description: Which IEEE paper or `eads.*` module is the question about?
  - type: textarea
    id: context
    attributes:
      label: Additional context
