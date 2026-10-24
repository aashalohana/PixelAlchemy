
import base64
import io
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, ImageOps

# Load the existing root .env without displaying its secrets.
APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")

OUTPUT_DIR = APP_DIR / "generated_images"
OUTPUT_DIR.mkdir(exist_ok=True)

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
MODEL = "@cf/black-forest-labs/flux-1-schnell"

API_URL = (
    "https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/{MODEL}"
)

STYLES = {
    "Cinematic": "cinematic composition, dramatic lighting, rich atmosphere, film still",
    "Photorealistic": "photorealistic, natural textures, realistic lighting, fine details",
    "Anime": "high-quality anime illustration, expressive details, beautiful color design",
    "Digital Art": "professional digital artwork, polished rendering, intricate details",
    "Fantasy": "fantasy concept art, atmospheric lighting, imaginative world, epic detail",
    "Minimalist": "minimalist composition, refined shapes, restrained colors, clean design",
}

# Frontend labels are mapped to numeric width:height ratios.
RATIOS = {
    "1:1": (1, 1),
    "2:3": (2, 3),
    "3:2": (3, 2),
    "16:9": (16, 9),
    "9:16": (9, 16),
    "Square · 1:1": (1, 1),
    "Portrait · 2:3": (2, 3),
    "Landscape · 3:2": (3, 2),
    "Wide · 16:9": (16, 9),
    "Story · 9:16": (9, 16),
}

app = Flask(__name__)


def crop_to_ratio(image, ratio):
    target_w, target_h = ratio
    target_ratio = target_w / target_h
    width, height = image.size

    if abs((width / height) - target_ratio) < 0.01:
        return image

    if width / height > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))

    new_height = int(width / target_ratio)
    top = (height - new_height) // 2
    return image.crop((0, top, width, top + new_height))


def image_history():
    files = sorted(
        OUTPUT_DIR.glob("pixelalchemy_*.png"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return [
        {
            "url": f"/images/{path.name}",
            "name": path.name,
            "createdAt": datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat(timespec="seconds"),
        }
        for path in files[:12]
    ]


@app.get("/api/health")
def health():
    return jsonify({"success": True, "message": "PixelAlchemy API is running"})


@app.get("/api/history")
def history():
    return jsonify({"success": True, "history": image_history()})


@app.get("/images/<path:filename>")
def serve_image(filename):
    # Only serve files from the generated images directory.
    return send_from_directory(OUTPUT_DIR, filename)


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}

    prompt = str(data.get("prompt", "")).strip()
    style = str(data.get("style", "Cinematic")).strip()
    ratio_label = str(data.get("ratio", "1:1")).strip()

    if not prompt:
        return jsonify({"success": False, "error": "Please enter an image prompt."}), 400

    if len(prompt) > 1500:
        return jsonify({"success": False, "error": "Prompt must be 1,500 characters or fewer."}), 400

    if style not in STYLES:
        style = "Cinematic"

    if ratio_label not in RATIOS:
        ratio_label = "1:1"

    if not ACCOUNT_ID or not API_TOKEN:
        return jsonify({
            "success": False,
            "error": "Cloudflare configuration is missing. Check your local .env file."
        }), 500

    full_prompt = f"{prompt}. Visual style: {STYLES[style]}."
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    started = time.time()

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"prompt": full_prompt},
            timeout=180,
        )

        if not response.ok:
            return jsonify({
                "success": False,
                "error": f"Cloudflare image generation failed (HTTP {response.status_code}).",
            }), 502

        content_type = response.headers.get("content-type", "").lower()

        if "image/" in content_type:
            image_bytes = response.content
        else:
            result = response.json()
            image_data = result.get("result", {}).get("image")
            if not image_data:
                return jsonify({
                    "success": False,
                    "error": "Cloudflare did not return image data.",
                }), 502
            image_bytes = base64.b64decode(image_data)

        with Image.open(io.BytesIO(image_bytes)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")

        image = crop_to_ratio(image, RATIOS[ratio_label])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pixelalchemy_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        output_path = OUTPUT_DIR / filename
        image.save(output_path, format="PNG", optimize=True)

        return jsonify({
            "success": True,
            "image": f"/images/{filename}",
            "style": style,
            "ratio": ratio_label,
            "width": image.width,
            "height": image.height,
            "generationSeconds": round(time.time() - started, 1),
            "history": image_history(),
        })

    except requests.Timeout:
        return jsonify({
            "success": False,
            "error": "Image generation timed out. Please try again.",
        }), 504
    except requests.RequestException:
        return jsonify({
            "success": False,
            "error": "Could not connect to the image service. Please try again.",
        }), 502
    except Exception as exc:
        app.logger.exception("Image generation failed")
        return jsonify({
            "success": False,
            "error": f"Image processing failed ({type(exc).__name__}). Check the backend terminal.",
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
