import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
MODEL = "@cf/black-forest-labs/flux-1-schnell"

STYLES = {
    "Cinematic": "cinematic lighting, dramatic composition, film still",
    "Photorealistic": "photorealistic, realistic textures, professional photography",
    "Anime": "anime illustration, expressive details, beautiful colors",
    "Digital Art": "high-quality digital art, detailed illustration",
    "Fantasy": "fantasy concept art, magical atmosphere, intricate details",
    "Minimalist": "minimalist composition, clean shapes, elegant simplicity",
}

CUSTOM_CSS = """
:root {
    --bg: #090a14;
    --panel: #101225;
    --panel2: #15182d;
    --border: #292d4c;
    --text: #f5f3ff;
    --muted: #a5a8c5;
    --purple: #9b5cff;
}

.gradio-container {
    max-width: 1500px !important;
    margin: auto !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: Inter, Segoe UI, Arial, sans-serif !important;
}

body, .main, .wrap, .contain {
    background: var(--bg) !important;
    color: var(--text) !important;
}

#topbar {
    padding: 20px 8px 25px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}

#brand {
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -1.1px;
    color: #fff;
}

#brand span { color: #b58aff; }

#tagline {
    color: var(--muted);
    font-size: 13px;
    margin-top: 4px;
}

.panel {
    background: linear-gradient(145deg, #121529, #0d0f1e) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 22px !important;
}

h1, h2, h3, label, .prose {
    color: var(--text) !important;
}

h2 { letter-spacing: -.5px; }

p, .secondary {
    color: var(--muted) !important;
}

textarea, input, select {
    background: #0d1020 !important;
    color: var(--text) !important;
    border: 1px solid #303451 !important;
    border-radius: 11px !important;
}

textarea:focus, input:focus {
    border-color: var(--purple) !important;
    box-shadow: 0 0 0 1px var(--purple) !important;
}

button {
    border-radius: 11px !important;
    transition: all .2s ease !important;
}

#generate-btn {
    background: linear-gradient(100deg, #7440db, #a855f7) !important;
    color: white !important;
    border: 0 !important;
    min-height: 52px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 24px #7c3aed35 !important;
}

#generate-btn:hover {
    filter: brightness(1.12);
}

#preview-image {
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
}

#preview-box {
    background: radial-gradient(ellipse at center, #21163e 0%, #101225 48%, #090a14 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px;
}

#status-box {
    background: #15172b;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
}

#details-box {
    background: #101225;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}

footer { color: var(--muted) !important; }

@media (max-width: 768px) {
    #brand { font-size: 24px; }
    .panel { padding: 15px !important; }
}
"""


def generate_image(prompt, style, aspect_ratio):
    prompt = (prompt or "").strip()

    if not prompt:
        return None, "Please enter an image description first.", "No image generated yet."

    if not ACCOUNT_ID or not API_TOKEN:
        return (
            None,
            "Cloudflare credentials missing. Check your local .env file.",
            "Generation unavailable."
        )

    style_instruction = STYLES.get(style, STYLES["Cinematic"])
    full_prompt = (
        f"{prompt}. Art direction: {style_instruction}. "
        "High-quality composition, carefully rendered details."
    )

    # Cloudflare FLUX Schnell currently accepts a prompt.
    # Aspect ratio is shown in the interface; this endpoint's dimensions
    # are not being changed unless supported by the model API.
    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{ACCOUNT_ID}/ai/run/{MODEL}"
    )

    payload = {"prompt": full_prompt}
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()

        if "image/" in content_type:
            image_bytes = data
        else:
            result = json.loads(data.decode("utf-8"))
            image_data = result.get("result", {}).get("image")

            if not result.get("success") or not image_data:
                errors = result.get("errors", [])
                return None, f"Cloudflare returned no image. Details: {errors}", ""

            if image_data.startswith("data:") and "," in image_data:
                image_data = image_data.split(",", 1)[1]

            image_bytes = base64.b64decode(image_data)

        output_dir = BASE_DIR / "generated_images"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "pixelalchemy_latest.png"
        output_path.write_bytes(image_bytes)

        details = (
            f"**Prompt:** {prompt}\n\n"
            f"**Style:** {style}\n\n"
            f"**Selected aspect ratio:** {aspect_ratio}\n\n"
            f"**Model:** FLUX.1 Schnell"
        )

        return str(output_path), "Image generated successfully.", details

    except urllib.error.HTTPError as error:
        try:
            message = error.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            message = "No additional details available."

        return None, f"Cloudflare API error ({error.code}): {message}", ""

    except Exception as error:
        return None, f"Generation failed: {type(error).__name__}: {error}", ""


with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="violet",
        secondary_hue="purple",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "Arial", "sans-serif"],
    ),
    css=CUSTOM_CSS,
    title="PixelAlchemy | AI Image Studio",
) as demo:

    gr.HTML("""
    <div id="topbar">
      <div id="brand">✧ Pixel<span>Alchemy</span></div>
      <div id="tagline">AI IMAGE STUDIO &nbsp;·&nbsp; Turn imagination into visual art</div>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=4, min_width=320):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## ✦ Create your artwork")
                gr.Markdown("Describe your vision, choose a style, and bring it to life.")

                prompt = gr.Textbox(
                    label="01  ·  Describe your imagination",
                    placeholder="A magical city floating above the clouds at sunset...",
                    lines=5,
                    max_lines=8,
                )

                style = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value="Cinematic",
                    label="02  ·  Art style",
                )

                aspect_ratio = gr.Radio(
                    choices=[
                        "Square (1:1)",
                        "Portrait (2:3)",
                        "Landscape (3:2)",
                    ],
                    value="Square (1:1)",
                    label="03  ·  Aspect ratio",
                )

                create_btn = gr.Button(
                    "✦  Generate Image",
                    variant="primary",
                    elem_id="generate-btn",
                )

                gr.Markdown(
                    "🔒 Your API credentials stay in your local `.env` file."
                )

        with gr.Column(scale=6, min_width=360):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## Studio Preview")
                status = gr.Markdown(
                    "✨ **Your next masterpiece starts with an idea.**\n\n"
                    "Enter a prompt and select your preferred style."
                )

                result_image = gr.Image(
                    label="Generated artwork",
                    type="filepath",
                    interactive=False,
                    elem_id="preview-image",
                )

                details = gr.Markdown(
                    "*Your prompt details will appear here after generation.*"
                )

                download = gr.File(
                    label="Download your artwork",
                    interactive=False,
                )

    def create_and_display(prompt_text, selected_style, selected_ratio):
        image_path, message, image_details = generate_image(
            prompt_text, selected_style, selected_ratio
        )
        download_path = image_path if image_path else None
        return image_path, message, image_details, download_path

    create_btn.click(
        fn=create_and_display,
        inputs=[prompt, style, aspect_ratio],
        outputs=[result_image, status, details, download],
    )

    gr.HTML("""
    <div style="text-align:center;padding:22px;color:#9295b4;font-size:12px">
      PixelAlchemy &nbsp;·&nbsp; AI Image Studio &nbsp;·&nbsp; Powered by Cloudflare AI
    </div>
    """)


if __name__ == "__main__":
    demo.queue().launch()