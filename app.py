
import base64
import io
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
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

RATIOS = {
    "Square · 1:1": (1, 1),
    "Portrait · 2:3": (2, 3),
    "Landscape · 3:2": (3, 2),
    "Wide · 16:9": (16, 9),
    "Story · 9:16": (9, 16),
}


def get_history():
    files = sorted(
        OUTPUT_DIR.glob("pixelalchemy_*.png"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return [str(path) for path in files[:12]]


def crop_to_ratio(image, ratio):
    """Center-crop the generated image to the selected aspect ratio."""
    target_w, target_h = ratio
    target_ratio = target_w / target_h
    width, height = image.size
    current_ratio = width / height

    if abs(current_ratio - target_ratio) < 0.01:
        return image

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))

    return image


def generate_image(prompt, style, aspect_ratio):
    prompt = (prompt or "").strip()

    if not prompt:
        return None, "Enter a prompt to begin.", "Your prompt is empty.", get_history(), None

    if len(prompt) > 1500:
        return None, "Prompt is too long.", "Please keep your prompt under 1,500 characters.", get_history(), None

    if not ACCOUNT_ID or not API_TOKEN:
        return None, "Configuration needed.", "Check your local .env file. Do not share your API credentials.", get_history(), None

    style_description = STYLES.get(style, STYLES["Cinematic"])
    full_prompt = f"{prompt}. Visual style: {style_description}."

    payload = {"prompt": full_prompt}
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    started = time.time()

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=180,
        )

        if not response.ok:
            try:
                error_data = response.json()
                error_message = json.dumps(error_data.get("errors", error_data))[:900]
            except ValueError:
                error_message = response.text[:900]

            return (
                None,
                f"Generation failed · HTTP {response.status_code}",
                f"Cloudflare response: {error_message}",
                get_history(),
                None,
            )

        content_type = response.headers.get("content-type", "").lower()

        if "image/" in content_type:
            image_bytes = response.content
        else:
            try:
                result = response.json()
            except ValueError:
                return None, "Unexpected response.", "The image service returned an unsupported response.", get_history(), None

            image_data = result.get("result", {}).get("image")

            if not image_data:
                return (
                    None,
                    "No image returned.",
                    json.dumps(result)[:1000],
                    get_history(),
                    None,
                )

            image_bytes = base64.b64decode(image_data)

        with Image.open(io.BytesIO(image_bytes)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")

        ratio_label = aspect_ratio if aspect_ratio in RATIOS else "Square · 1:1"
        image = crop_to_ratio(image, RATIOS[ratio_label])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        output_path = OUTPUT_DIR / f"pixelalchemy_{timestamp}_{unique_id}.png"
        image.save(output_path, format="PNG", optimize=True)

        elapsed = time.time() - started
        width, height = image.size

        details = (
            f"Style: {style}\n"
            f"Aspect ratio: {ratio_label}\n"
            f"Output size: {width} × {height} px\n"
            f"Generation time: {elapsed:.1f} seconds\n"
            f"Model: FLUX.1 schnell\n\n"
            "Note: the selected ratio is applied by center-cropping "
            "the generated image. The model itself generates the initial image."
        )

        return (
            str(output_path),
            "Image created successfully",
            details,
            get_history(),
            str(output_path),
        )

    except requests.Timeout:
        return None, "Request timed out.", "The image service took too long. Please try again.", get_history(), None
    except requests.RequestException as exc:
        return None, "Connection error.", str(exc)[:700], get_history(), None
    except Exception as exc:
        return None, "Something went wrong.", f"{type(exc).__name__}: {str(exc)[:700]}", get_history(), None


CSS = """
:root {
    --studio-bg: #0b0c10;
    --studio-panel: #111319;
    --studio-panel-soft: #171922;
    --studio-border: #292b36;
    --studio-text: #f3f2f7;
    --studio-muted: #9699a9;
    --studio-accent: #a78bfa;
}

.gradio-container {
    max-width: 1440px !important;
    margin: 0 auto !important;
    background:
        radial-gradient(ellipse at 78% 0%, rgba(124, 92, 210, .11), transparent 36%),
        var(--studio-bg) !important;
    color: var(--studio-text) !important;
    font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
}

body, .main, .wrap {
    background: var(--studio-bg) !important;
}

#app-header {
    padding: 22px 4px 25px;
    border-bottom: 1px solid var(--studio-border);
    margin-bottom: 24px;
}

#brand {
    font-size: 26px;
    line-height: 1.2;
    font-weight: 750;
    letter-spacing: -1px;
    color: #faf9ff;
}

#brand span {
    color: var(--studio-accent);
}

#tagline {
    margin-top: 7px;
    color: var(--studio-muted);
    font-size: 13px;
}

#workspace-title {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #b8a6f7;
    margin: 0 0 14px;
}

.studio-panel {
    background: rgba(17, 19, 25, .94);
    border: 1px solid var(--studio-border);
    border-radius: 16px;
    padding: 21px !important;
}

.studio-heading {
    font-size: 17px;
    font-weight: 650;
    letter-spacing: -.3px;
    margin-bottom: 5px;
    color: var(--studio-text);
}

.studio-subtitle {
    font-size: 12px;
    line-height: 1.6;
    color: var(--studio-muted);
    margin-bottom: 20px;
}

label, .label-wrap span {
    color: #dedde7 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

textarea, input, .wrap input, .wrap textarea {
    background: #0d0f14 !important;
    border: 1px solid #30323e !important;
    border-radius: 10px !important;
    color: #f6f4fb !important;
}

textarea:focus, input:focus {
    border-color: #8870d2 !important;
    box-shadow: 0 0 0 2px rgba(167, 139, 250, .10) !important;
}

button.primary {
    background: linear-gradient(110deg, #8d75dc, #b09af4) !important;
    color: #171321 !important;
    border: 0 !important;
    border-radius: 10px !important;
    font-weight: 750 !important;
    min-height: 46px !important;
    transition: filter .2s ease, transform .2s ease;
}

button.primary:hover {
    filter: brightness(1.08);
}

button.secondary, .secondary {
    background: #1b1d26 !important;
    border: 1px solid #333541 !important;
    color: #e9e5f5 !important;
    border-radius: 9px !important;
}

#preview-frame {
    min-height: 460px;
    background:
        radial-gradient(ellipse at center, rgba(100, 83, 155, .10), transparent 60%),
        #0c0e13;
    border: 1px solid #292b36;
    border-radius: 14px;
    padding: 12px !important;
}

#preview-frame img {
    object-fit: contain !important;
    border-radius: 8px !important;
}

#status-panel {
    border: 1px solid #292b36;
    background: #111319;
    border-radius: 10px;
    padding: 12px 14px !important;
    color: #c9c5d8;
    font-size: 12px;
}

#details-panel textarea {
    font-size: 12px !important;
    line-height: 1.7 !important;
    color: #b9b6c8 !important;
}

#history-title {
    font-size: 17px;
    font-weight: 650;
    margin: 32px 0 12px;
}

footer {
    display: none !important;
}

@media (max-width: 760px) {
    #preview-frame { min-height: 280px; }
    #app-header { padding: 15px 2px 20px; }
    .studio-panel { padding: 15px !important; }
}
"""


with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="violet",
        neutral_hue="slate",
        font=["Inter", "Arial", "sans-serif"],
    ),
    css=CSS,
    title="PixelAlchemy — AI Image Studio",
) as demo:

    gr.HTML("""
    <div id="app-header">
        <div id="brand">Pixel<span>Alchemy</span></div>
        <div id="tagline">AI IMAGE STUDIO &nbsp; / &nbsp; Turn ideas into visuals.</div>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=4, min_width=300):
            with gr.Group(elem_classes=["studio-panel"]):
                gr.HTML('<div id="workspace-title">01 &nbsp; / &nbsp; CREATE</div>')
                gr.HTML('<div class="studio-heading">Describe your vision</div>')
                gr.HTML('<div class="studio-subtitle">Write a clear description of the image you want to create.</div>')

                prompt = gr.Textbox(
                    label="IMAGE PROMPT",
                    placeholder="A quiet Japanese tea house in a misty forest, soft morning light, cinematic composition...",
                    lines=7,
                    max_lines=12,
                    max_length=1500,
                )

                style = gr.Dropdown(
                    choices=list(STYLES.keys()),
                    value="Cinematic",
                    label="VISUAL STYLE",
                )

                aspect_ratio = gr.Radio(
                    choices=list(RATIOS.keys()),
                    value="Square · 1:1",
                    label="ASPECT RATIO",
                )

                generate_btn = gr.Button(
                    "Generate image",
                    variant="primary",
                    size="lg",
                )

                gr.HTML(
                    '<div class="studio-subtitle" style="margin:12px 0 0">'
                    'Powered by Cloudflare Workers AI. Availability and usage limits may apply.'
                    '</div>'
                )

        with gr.Column(scale=6, min_width=320):
            with gr.Group(elem_classes=["studio-panel"]):
                gr.HTML('<div id="workspace-title">02 &nbsp; / &nbsp; CANVAS</div>')
                gr.HTML('<div class="studio-heading">Your creation</div>')
                gr.HTML('<div class="studio-subtitle">Your generated image appears here, ready to preview and save.</div>')

                preview = gr.Image(
                    label="STUDIO PREVIEW",
                    type="filepath",
                    interactive=False,
                    show_label=False,
                    height=460,
                    elem_id="preview-frame",
                )

                status = gr.Textbox(
                    value="Ready when you are. Describe an image to get started.",
                    label="STATUS",
                    interactive=False,
                    lines=2,
                    elem_id="status-panel",
                )

                download_file = gr.File(
                    label="DOWNLOAD YOUR IMAGE",
                    interactive=False,
                )

                details = gr.Textbox(
                    label="GENERATION DETAILS",
                    interactive=False,
                    lines=5,
                    elem_id="details-panel",
                )

    gr.HTML('<div id="history-title">Recent creations</div>')
    gr.HTML('<div class="studio-subtitle">Your latest 12 images saved on this machine.</div>')

    history = gr.Gallery(
        value=get_history,
        label="IMAGE HISTORY",
        columns=4,
        height="auto",
        object_fit="contain",
        show_label=False,
        allow_preview=True,
    )

    generate_btn.click(
        fn=generate_image,
        inputs=[prompt, style, aspect_ratio],
        outputs=[preview, status, details, history, download_file],
    )

    prompt.submit(
        fn=generate_image,
        inputs=[prompt, style, aspect_ratio],
        outputs=[preview, status, details, history, download_file],
    )


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
