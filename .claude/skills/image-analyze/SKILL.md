---
name: image-analyze
description: >
  Deep structured image analysis using Claude's native vision. Use this skill
  whenever the user asks to analyze, inspect, describe, review, or understand
  an image or set of images. Also triggers on: "what's in this image",
  "look at this screenshot", "analyze this photo", "examine this image",
  "tell me about this image", "read this image", "interpret this visual".
triggers:
  - analyze image
  - analyze this image
  - look at this image
  - examine this image
  - describe this image
  - what is in this image
  - review this screenshot
  - interpret this visual
  - image analysis
  - vision analysis
---

# Image Analysis Skill

You are performing a deep structured analysis of one or more images using your
native vision capabilities. Follow this process exactly.

## Step 1 — Gather inputs

Collect the image(s) from the user. Accepted forms:
- File paths on disk (read them directly)
- URLs (fetch them)
- Base64 data URIs
- Images pasted directly into the conversation

If no image was provided, ask for one before proceeding.

## Step 2 — Identify the analysis type

Pick the most appropriate analysis mode based on context:

| Mode | When to use |
|------|-------------|
| **General** | No specific goal stated — full description |
| **Document** | Photo of a form, letter, receipt, PDF scan |
| **Chart/Graph** | Bar chart, line graph, pie chart, data visualization |
| **Screenshot** | UI, terminal output, code editor, website |
| **Comparison** | 2+ images to diff or compare |
| **OCR** | Extract all readable text verbatim |
| **Anomaly** | Find defects, errors, or outliers |

If ambiguous, ask one clarifying question, then proceed.

## Step 3 — Analyze

Work through each image systematically:

### For General / Description mode
1. **Overview** — What is this image of? (1–2 sentences)
2. **Objects & Elements** — List all significant objects, people, text, logos
3. **Spatial layout** — How are elements arranged? (foreground/background, grid, etc.)
4. **Colors & Style** — Dominant colors, visual style, lighting
5. **Context & Purpose** — What is this image for? What story does it tell?
6. **Notable details** — Anything unusual, hidden, or easy to miss

### For Document mode
1. Extract all visible text verbatim (preserve structure)
2. Identify document type (invoice, contract, form, etc.)
3. Extract key fields: dates, names, amounts, identifiers
4. Flag any redacted, blurry, or illegible sections

### For Chart/Graph mode
1. Identify chart type and title
2. Extract axis labels, units, and legend
3. Extract all data points or summarize trends
4. State the key insight the chart conveys
5. Note any misleading elements (truncated axis, missing labels, etc.)

### For Screenshot mode
1. Identify the application or website
2. Describe the UI state (what page/screen, what's selected/open)
3. Extract any visible text, error messages, or notifications
4. Note any anomalies (errors, warnings, unexpected states)

### For Comparison mode (2+ images)
1. Analyze each image individually (brief)
2. List what is **the same** across images
3. List what is **different** (be specific: position, color, text, missing elements)
4. Summarize the significance of the differences

### For OCR mode
- Output all text exactly as it appears, preserving line breaks and structure
- Use `---` to separate distinct text regions
- Note confidence issues with `[unclear: ...]`

### For Anomaly mode
1. Describe what the normal/expected state would be
2. List each anomaly found with location and description
3. Assess severity: low / medium / high

## Step 4 — Format output

Use this structure for your response:

```
## Image Analysis

**Mode:** [General | Document | Chart | Screenshot | Comparison | OCR | Anomaly]
**Images analyzed:** [count]

---

[Analysis content based on mode above]

---

### Summary
[1–3 sentence takeaway]

### Confidence notes
[Any areas where the image was unclear, low-res, partially obscured, etc.]
```

## Multiple images

When multiple images are provided:
- Analyze them jointly when comparison is the goal
- Analyze them individually when each stands alone, then provide a combined summary
- Label each as `Image 1`, `Image 2`, etc.

## Limitations to state proactively

Always mention if:
- The image is too low resolution to read text clearly
- Parts of the image are obscured, cropped, or blurry
- You cannot identify a person's identity (you never attempt this)
- The content requires domain expertise to fully interpret (medical, legal, technical)
