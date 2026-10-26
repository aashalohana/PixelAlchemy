
import { useEffect, useState } from "react";
import "./App.css";

const styles = [
  {
    name: "Cinematic",
    image: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=240&h=160&fit=crop",
  },
  {
    name: "Photorealistic",
    image: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=240&h=160&fit=crop",
  },
  {
    name: "Anime",
    image: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=240&h=160&fit=crop",
  },
  {
    name: "Digital Art",
    image: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=240&h=160&fit=crop",
  },
  {
    name: "Fantasy",
    image: "https://images.unsplash.com/photo-1511497584788-876760111969?w=240&h=160&fit=crop",
  },
  {
    name: "Minimalist",
    image: "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=240&h=160&fit=crop",
  },
];

const ratios = ["1:1", "2:3", "3:2", "16:9", "9:16"];


 
function PixelAlchemyLogo() {
  return (
    <svg
      className="brand-logo"
      viewBox="0 0 64 64"
      width="44"
      height="44"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="PixelAlchemy logo"
      role="img"
    >
      <defs>
        <linearGradient
          id="crystalGradient"
          x1="12"
          y1="50"
          x2="49"
          y2="8"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0%" stopColor="#A855F7" />
          <stop offset="55%" stopColor="#818CF8" />
          <stop offset="100%" stopColor="#67E8F9" />
        </linearGradient>
      </defs>

      <path
        d="M32 7 L47 23 L32 49 L17 23 Z"
        fill="url(#crystalGradient)"
      />
      <path
        d="M17 23 L32 27 L47 23 M32 7 V49"
        stroke="#FFFFFF"
        strokeOpacity="0.75"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M49 5 L52 13 L60 16 L52 19 L49 27 L46 19 L38 16 L46 13 Z"
        fill="#F0ABFC"
      />
      <circle cx="12" cy="42" r="2.5" fill="#67E8F9" />
      <circle cx="53" cy="38" r="1.8" fill="#A78BFA" />
    </svg>
  );
}


function App() {
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("Cinematic");
  const [ratio, setRatio] = useState("1:1");
  const [image, setImage] = useState(null);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState("Your creative space is ready.");
  const [loading, setLoading] = useState(false);
  const [imageDetails, setImageDetails] = useState(null);

  async function loadHistory() {
    try {
      const response = await fetch("/api/history");
      const data = await response.json();

      if (response.ok && data.success) {
        setHistory(data.history || []);
      }
    } catch {
      setStatus("Could not connect to the local backend yet.");
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function generateImage() {
    if (!prompt.trim()) {
      setStatus("Write a prompt before generating your image.");
      return;
    }

    setLoading(true);
    setStatus("Creating your image. This may take a little while...");

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt.trim(), style, ratio }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Image generation failed.");
      }

      const imageUrl = `${data.image}?t=${Date.now()}`;
     setImage(imageUrl);
setHistory(data.history || []);

setImageDetails({
  prompt: prompt.trim(),
  style: style,
  ratio: ratio,
  width: data.width,
  height: data.height,
  generationSeconds: data.generationSeconds,
});

setStatus(
  `Image created · ${data.width} × ${data.height} px · ${data.generationSeconds}s`
);
    } catch (error) {
      setStatus(error.message || "Could not generate the image. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function downloadImage() {
    if (!image) return;

    const link = document.createElement("a");
    link.href = image;
    link.download = "pixelalchemy-creation.png";
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  function selectHistoryItem(item) {
    setImage(item.url);
    setStatus(`Selected saved creation · ${item.name}`);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="PixelAlchemy home">
          <PixelAlchemyLogo />
          <span className="brand-name">
            Pixel<span className="brand-accent">Alchemy</span>
          </span>
        </a>

<nav className="topbar-center main-navigation" aria-label="Main navigation">
  <a
    className="nav-link active"
    href="#create"
    onClick={(event) => {
      event.preventDefault();
      document.getElementById("create")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }}
  >
    <span>✧</span> Create
  </a>

  <a
    className="nav-link"
    href="#gallery"
    onClick={(event) => {
      event.preventDefault();
      document.getElementById("gallery")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }}
  >
    <span>▣</span> Gallery
  </a>

  <a
    className="nav-link"
    href="#about"
    onClick={(event) => {
      event.preventDefault();
      document.getElementById("about")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }}
  >
    <span>ⓘ</span> About
  </a>
</nav>

        <div className="topbar-right">
          <span className="model-label">IMAGE STUDIO</span>
          <div className="avatar" aria-label="PixelAlchemy">PA</div>
        </div>
      </header>

      <main className="workspace">
        <aside id="create" className="control-panel">
          <div className="eyebrow">YOUR CREATIVE WORKSPACE</div>
          <h1>Imagine<br />something <span>beautiful.</span></h1>
          <p className="intro">
            Turn your ideas into striking visuals. Describe it, shape the
            style, and bring it to life.
          </p>

          <div className="section-divider" />

          <label className="field-label" htmlFor="prompt">
            YOUR PROMPT
            <span className="optional">REQUIRED</span>
          </label>

          <textarea
            id="prompt"
            className="prompt-input"
            placeholder="A quiet Japanese tea house surrounded by a misty forest, soft morning light..."
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            maxLength={1500}
            rows={6}
          />

          <div className="prompt-footer">
            <span>Be descriptive for better results</span>
            <span>{prompt.length}/1500</span>
          </div>

<div className="form-section">
  <div className="field-label">CHOOSE AN ART STYLE</div>

  <div className="style-grid">
    {styles.map((item) => (
      <button
        key={item.name}
        type="button"
        className={`style-option ${
          style === item.name ? "selected" : ""
        }`}
        onClick={() => setStyle(item.name)}
        aria-pressed={style === item.name}
      >
        <img src={item.image} alt="" />
        <span>{item.name}</span>
        {style === item.name && (
          <span className="style-check">✓</span>
        )}
      </button>
    ))}
  </div>
</div>


          <div className="form-section">
            <div className="field-label">ASPECT RATIO</div>
            <div className="ratio-grid">
              {ratios.map((item) => (
                <button
                  key={item}
                  type="button"
                  className={`ratio-option ${ratio === item ? "selected" : ""}`}
                  onClick={() => setRatio(item)}
                  aria-pressed={ratio === item}
                >
                  <span className={`ratio-icon ratio-${item.replace(":", "-")}`} />
                  <span>{item}</span>
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            className="generate-button"
            onClick={generateImage}
            disabled={loading}
          >
            <span className="sparkle" aria-hidden="true">✧</span>
            {loading ? "Creating your image..." : "Generate image"}
            <span className="button-arrow" aria-hidden="true">↗</span>
          </button>

          <div className="privacy-note">
            <span className="lock-icon" aria-hidden="true">◇</span>
            Your prompts stay in your workspace.
          </div>
        </aside>

        <section className="canvas-area">
          <div className="canvas-toolbar">
            <div>
              <div className="eyebrow">CANVAS / 01</div>
              <h2>Your creation</h2>
            </div>
            <div className="canvas-actions">
              <span className="ratio-badge">{ratio}</span>
              <button
                type="button"
                className="download-button"
                onClick={downloadImage}
                disabled={!image}
              >
                ↓ <span>Download</span>
              </button>
            </div>
          </div>

          <div className={`preview-canvas ${image ? "has-image" : ""}`}>
            {image ? (
              <img className="generated-image" src={image} alt={prompt || "Generated artwork"} />
            ) : (
              <div className="empty-state">
                <div className="artwork-frame">
                  <div className="artwork-glow" />
                  <div className="artwork-sun" />
                  <div className="artwork-mountain mountain-back" />
                  <div className="artwork-mountain mountain-front" />
                  <div className="artwork-water" />
                  <div className="artwork-reflection" />
                </div>
                <div className="empty-title">Your next masterpiece starts here.</div>
                <p>
                  Enter a prompt and generate an image to see your idea
                  come to life.
                </p>
                <div className="canvas-hint">
                  <span className="hint-dot" />
                  WAITING FOR YOUR FIRST CREATION
                </div>
              </div>
            )}
          </div>

         
{image && imageDetails && (
  <section className="prompt-details">
    <div className="prompt-details-heading">
      <div>
        <div className="eyebrow">CREATION INFORMATION</div>
        <h2>Prompt Details</h2>
      </div>
      <span className="details-badge">Generated</span>
    </div>

    <div className="details-prompt">
      <div className="details-label">YOUR PROMPT</div>
      <p>{imageDetails.prompt}</p>
    </div>

    <div className="details-grid">
      <div className="detail-card">
        <span className="details-label">VISUAL STYLE</span>
        <strong>{imageDetails.style}</strong>
      </div>

      <div className="detail-card">
        <span className="details-label">ASPECT RATIO</span>
        <strong>{imageDetails.ratio}</strong>
      </div>

      <div className="detail-card">
        <span className="details-label">IMAGE DIMENSIONS</span>
        <strong>
          {imageDetails.width} × {imageDetails.height} px
        </strong>
      </div>

      <div className="detail-card">
        <span className="details-label">GENERATION TIME</span>
        <strong>{imageDetails.generationSeconds}s</strong>
      </div>
    </div>
  </section>
)}


          <section id="gallery" className="history-section">
            <div className="history-heading">
              <div>
                <div className="eyebrow">YOUR COLLECTION</div>
                <h2>Recent creations</h2>
              </div>
              <span className="history-count">{history.length} images</span>
            </div>

            {history.length ? (
              <div className="history-grid">
                {history.map((item, index) => (
                  <button
                    className="history-item"
                    key={item.name || `${item.url}-${index}`}
                    onClick={() => selectHistoryItem(item)}
                    aria-label={`View creation ${index + 1}`}
                  >
                    <img src={item.url} alt={`Creation ${index + 1}`} />
                  </button>
                ))}
              </div>
            ) : (
              <div className="history-empty">
                <span className="history-empty-icon">＋</span>
                <span>Your generated images will appear here.</span>
              </div>
            )}
          </section>
        </section>
      </main>

      <footer id="about" className="app-footer">
        <span>
          PIXELALCHEMY <span className="footer-dot">/</span> CREATIVE TOOLS
        </span>
        <span>Made for ideas worth seeing.</span>
      </footer>
    </div>
  );
}

export default App;
