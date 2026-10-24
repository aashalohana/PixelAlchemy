# PixelAlchemy — AI Image Studio

PixelAlchemy is an AI-powered image generation web application that transforms text prompts into images through a modern, user-friendly interface.

## Features

- Generate AI images from text prompts
- Multiple visual styles, including Cinematic, Photorealistic, Anime, Digital Art, Fantasy, and Minimalist
- Multiple aspect ratios for square, portrait, landscape, wide, and story formats
- Preview and download generated images
- Recent Creations gallery with locally saved generation history
- Responsive React frontend
- Flask REST API
- Cloudflare Workers AI integration using FLUX.1 Schnell
- Local environment-variable configuration for API credentials

## Technology Stack

**Frontend**
- React
- Vite
- JavaScript
- CSS

**Backend**
- Python
- Flask
- Requests
- Pillow
- python-dotenv

**AI Image Generation**
- Cloudflare Workers AI
- FLUX.1 Schnell

## Project Structure

```text
PixelAlchemy/
├── app.py
├── backend_api.py
├── requirements.txt
├── README.md
├── generated_images/
└── frontend/
    ├── public/
    ├── src/
    ├── package.json
    ├── package-lock.json
    └── vite.config.js
```

## Prerequisites

- Python 3.12
- Node.js and npm
- Cloudflare account with access to Workers AI
- Cloudflare Account ID and API token

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/aashalohana/PixelAlchemy.git
cd PixelAlchemy
```

### 2. Create and activate a Python virtual environment

On Windows:

```cmd
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```text
CLOUDFLARE_ACCOUNT_ID