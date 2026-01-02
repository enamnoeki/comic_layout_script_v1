# Webcomic Builder (Python)

This tool generates a **long vertical webcomic image** from a layout file.  
You control **canvas size, background, image sizes, and positioning** using numbers.

There is **no visual editor** the script renders once and exits.

---

## Requirements

- Python 3.9+
- Pillow (image library)

### Install Pillow
```
pip install pillow
```

### Set up your folders and files
```bash
project/
├─ build_webcomic.py
├─ layout.json
├─ assets/
│  ├─ panel1.png
│  ├─ panel2.png
│  ├─ bg_texture.png   (optional)
│  └─ bg_image.png     (optional)
└─ output/
```

#### How It Works

`layout.json`
→ controls how all the images are arranged. Edit the numbers there to change size, position, and more. 

`build_webcomic.py`
→ reads the layout and exports the image

`slice_webcomic.py`
→ reads image in the layout folder and slices it. 

`output`
→ stores the image once it's exported

### Running the Script

From the project folder, run this in the terminal:
`python build_webcomic.py --layout layout.json`

If successful, you’ll see:

`✅ Saved: output/webcomic.png (800xXXXX)`

### layout.json

## Overview
Canvas Size
```
"canvas": {
  "width": 800,
  "height": 2400
}
```
- Change these values to set the width and height. This is for a full webcomic before it gets sliced.

### Background Options in `layout.json`

#### Solid color
```
"background": {
  "type": "solid",
  "color": "#ffffff"
}
```
#### Seamless pattern
```
"background": {
  "type": "pattern",
  "file": "assets/bg_texture.png",
  "scale": 1.0
}
```

#### Single image
```
"background": {
  "type": "image",
  "file": "assets/bg_image.png",
  "mode": "cover"
}
```

#### Modes
`cover` – fills canvas (may crop)
`contain` – fits inside canvas
`stretch` – distorts to fill

### Default Image Size
```
"defaults": {
  "w": 700,
  "h": 600,
  "fit": "contain"
}
```
- Applies to all images unless overridden.

### Adding Images
```
"items": [
  { "file": "assets/panel1.png", "x": 50, "y": 80 },
  { "file": "assets/panel2.png", "x": 50, "y": 860 }
]
```
- x, y are pixel coordinates
- (0,0) is top-left of the canvas

#### Image Overrides (Optional)

Override size or fit for a specific image:
```
{
  "file": "assets/panel3.png",
  "x": 40,
  "y": 1600,
  "w": 760,
  "h": 900,
  "fit": "contain"
}
```
Use overrides only when an image doesn’t fit well.

### Layer Order (Important)
Items go in order. If they overlap, the image on top will show in the front. The image at the bottom will be behind. 

```
 "items": [
    { "file": "assets/panel1.png", "x": 50, "y": 80 },
    { "file": "assets/panel2.png", "x": 50, "y": 860 },
    { "file": "assets/panel1.png", "x": 50, "y": 1640, "w": 700, "h": 600 }
  ],
```

### Export Settings
You can change here to change the size of the final document.
```
"export": {
  "file": "output/webcomic.png"
}
```

The script exports a single PNG image.

## Typical Workflow

1. Draw panels
2. Save images into `assets/`
a. Label them as `bg`, `panel`, and `footer or cta` to make it easier to identify
3. Edit layout.json (positions, sizes)
4. Run the script
a. For making the whole file - `python build_webcomic.py --layout layout.json`
b. For slicing the file - `python slice_webcomic.py --input output/webcomic.png --slice-height 1200 --overlap 0`
5. Review output
6. Adjust numbers if needed