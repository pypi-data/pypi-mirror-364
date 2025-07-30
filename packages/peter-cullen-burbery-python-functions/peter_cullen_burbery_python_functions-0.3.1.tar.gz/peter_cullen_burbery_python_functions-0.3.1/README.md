# peter_cullen_burbery_python_functions

A small utility package by Peter Cullen Burbery that provides high-precision date/time formatting functions and image comparison tools.

## ✨ Features

### 📅 `date_time_functions`
- `date_time_stamp()`  
  Returns a precise timestamp string including:
  - Gregorian calendar date
  - Time with nanosecond precision
  - IANA time zone
  - ISO week format (e.g., `2025-W030-005`)
  - Ordinal day of the year

Example:
```text
2025-007-025 015.005.004.990819700 America/New_York 2025-W030-005 2025-206
```

---

### 🖼️ `image_functions`
- `compare_images(image_path_1, image_path_2)`  
  Compares two images using:
  - 🔐 SHA-256 hash
  - 🧮 Pixel-wise difference via `ImageChops`
  - 📏 Structural Similarity Index (SSIM)
  - 📊 ImageMagick absolute error metric (if available)

Outputs:
- Matching/difference status
- SSIM score
- Optional diff image (if images differ)

---

## 📦 Installation

```bash
pip install peter-cullen-burbery-python-functions
```

## 🧪 Example Usage

```python
from peter_cullen_burbery_python_functions.date_time_functions import date_time_stamp
from peter_cullen_burbery_python_functions.image_functions import compare_images

print("🕒 Timestamp:", date_time_stamp())
compare_images("image1.png", "image2.png")
```

---

## 🧑‍💻 Author

**Peter Cullen Burbery**

This utility library is part of a broader collection of tools for automation, data processing, and system utility scripting.