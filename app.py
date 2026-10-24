
import gradio as gr

CUSTOM_CSS = """

.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
    background: #0b0b12 !important;
    color: #f4f0ff !important;
}

.gradio-container,
.gradio-container .block,
.gradio-container .form,
.gradio-container .panel {
    color: #f4f0ff !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container select {
    background: #1b1728 !important;
    color: #f4f0ff !important;
    border: 1px solid #413354 !important;
}

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    color: #aaa0bc !important;
}

.gradio-container label,
.gradio-container .prose,
.gradio-container .markdown {
    color: #e8e0f5 !important;
}

.gradio-container button {
    border-radius: 10px !important;
}

.gradio-container .wrap {
    border-color: #302744 !important;
}
"""

def prepare_preview(prompt, style, aspect_ratio):
    prompt = (prompt or "").strip()

    if not prompt:
        return (
            "Please enter a description first.",
            f"**Style:** {style} · **Aspect ratio:** {aspect_ratio}"
        )

    return (
        "Your prompt is ready. AI image generation will be connected in the next step.",
        f"**Prompt:** {prompt}\n\n**Style:** {style} · **Aspect ratio:** {aspect_ratio}"
    )

with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="violet",
        secondary_hue="purple",
        neutral_hue="slate"
    ),
    css=CUSTOM_CSS,
    title="PixelAlchemy | AI Image Studio"
) as demo:

    gr.HTML("""
    <div id="hero">
        <h1>✦ PixelAlchemy</h1>
        <p>Turn your imagination into visual art.</p>
        <p>YOUR IDEAS · YOUR STYLE · YOUR CREATIVE STUDIO</p>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## ✨ Create your artwork")
                prompt = gr.Textbox(
                    label="Describe your imagination",
                    placeholder="A magical city floating above the clouds at sunset...",
                    lines=5
                )

                style = gr.Dropdown(
                    choices=[
                        "Cinematic",
                        "Photorealistic",
                        "Anime",
                        "Digital Art",
                        "Fantasy",
                        "Minimalist"
                    ],
                    value="Cinematic",
                    label="Choose an art style"
                )

                aspect_ratio = gr.Radio(
                    choices=["Square (1:1)", "Portrait (2:3)", "Landscape (3:2)"],
                    value="Square (1:1)",
                    label="Aspect ratio"
                )

                create_btn = gr.Button(
                    "✦ Prepare My Creation",
                    variant="primary",
                    elem_classes=["primary-btn"]
                )

            gr.Markdown(
                "🔒 **Your creative space**\n\n"
                "AI generation is not connected yet. No generated image will be "
                "claimed until a real image model is integrated."
            )

        with gr.Column(scale=6):
            with gr.Group(elem_classes=["panel"]):
                gr.Markdown("## 🖼️ Studio preview")
                status = gr.Markdown(
                    "Your next masterpiece starts with an idea.\n\n"
                    "Enter a prompt and prepare it to see your settings here."
                )
                details = gr.Markdown(
                    "*Your prompt details will appear here.*"
                )

    create_btn.click(
        fn=prepare_preview,
        inputs=[prompt, style, aspect_ratio],
        outputs=[status, details]
    )

    gr.Markdown(
        "<center>PixelAlchemy · AI Image Studio · Built with care</center>"
    )

if __name__ == "__main__":
    demo.launch()
