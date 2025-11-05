const API_BASE = window.APP_CONFIG?.apiBase ?? "http://localhost:8000/api";

const state = {
  products: [],
  videos: [],
  quotes: [],
  quoteIndex: 0,
  quoteTimer: null,
};

const selectors = {
  productGrid: document.querySelector("#productGrid"),
  videoGallery: document.querySelector("#videoGallery"),
  quoteText: document.querySelector("#quoteText"),
  quoteAuthor: document.querySelector("#quoteAuthor"),
  videoProductSelect: document.querySelector("#videoProductSelect"),
  toast: document.querySelector("#toast"),
};

const forms = {
  product: document.querySelector("#productForm"),
  video: document.querySelector("#videoForm"),
  quote: document.querySelector("#quoteForm"),
};

const buttons = {
  prevQuote: document.querySelector("#prevQuote"),
  nextQuote: document.querySelector("#nextQuote"),
  exploreCollection: document.querySelector("#exploreCollection"),
  watchKitchen: document.querySelector("#watchKitchen"),
  ctaButton: document.querySelector("#ctaButton"),
};

function showToast(message, variant = "info") {
  const toast = selectors.toast;
  toast.textContent = message;
  toast.dataset.variant = variant;
  toast.classList.add("show");
  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => toast.classList.remove("show"), 3200);
}

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const detail = errorBody.detail ?? response.statusText;
    throw new Error(detail || "Something went wrong");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function productCardTemplate(product) {
  const image = product.image_url ?? "https://images.unsplash.com/photo-1576511459011-0ca3d859c05b";
  return `
    <article class="product-card">
      <img class="product-card__image" src="${image}" alt="${product.name}" />
      <div class="product-card__body">
        <span class="product-card__category">${product.category ?? "Featured"}</span>
        <h3 class="product-card__title">${product.name}</h3>
        <p class="product-card__description">${product.description}</p>
        <div class="product-card__footer">
          <span class="product-card__price">$${product.price.toFixed(2)}</span>
          ${product.available ? '<span class="badge-availability">In Atelier</span>' : ""}
        </div>
      </div>
    </article>
  `;
}

function getEmbedUrl(url) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtube.com")) {
      const videoId = parsed.searchParams.get("v");
      if (videoId) return `https://www.youtube.com/embed/${videoId}`;
      const pathParts = parsed.pathname.split("/");
      const shortId = pathParts[pathParts.length - 1];
      if (shortId) return `https://www.youtube.com/embed/${shortId}`;
    }
    if (parsed.hostname.includes("youtu.be")) {
      return `https://www.youtube.com/embed${parsed.pathname}`;
    }
    if (parsed.hostname.includes("vimeo.com")) {
      const vimeoId = parsed.pathname.split("/").pop();
      return `https://player.vimeo.com/video/${vimeoId}`;
    }
    return url;
  } catch (err) {
    return url;
  }
}

function videoCardTemplate(video) {
  const embedUrl = getEmbedUrl(video.url);
  return `
    <article class="video-card">
      <iframe src="${embedUrl}" title="${video.title}" allowfullscreen></iframe>
      <div class="video-card__body">
        <h3 class="video-card__title">${video.title}</h3>
        ${video.description ? `<p class="video-card__description">${video.description}</p>` : ""}
        ${video.product_id ? `<span class="product-card__category">Product #${video.product_id}</span>` : ""}
      </div>
    </article>
  `;
}

function renderProducts() {
  selectors.productGrid.innerHTML = state.products.map(productCardTemplate).join("");
  renderVideoProductOptions();
}

function renderVideos() {
  selectors.videoGallery.innerHTML = state.videos.map(videoCardTemplate).join("");
}

function renderQuotes() {
  if (state.quotes.length === 0) {
    selectors.quoteText.textContent = "Add your first quote to inspire visitors.";
    selectors.quoteAuthor.textContent = "";
    return;
  }
  const current = state.quotes[state.quoteIndex];
  selectors.quoteText.textContent = `"${current.text}"`;
  selectors.quoteAuthor.textContent = current.author ? `— ${current.author}` : "— RarePeti Atelier";
}

function renderVideoProductOptions() {
  const select = selectors.videoProductSelect;
  const existing = select.value;
  select.innerHTML = '<option value="">No attachment</option>' +
    state.products.map((product) => `<option value="${product.id}">${product.name}</option>`).join("");
  if (existing) {
    select.value = existing;
  }
}

function startQuoteRotation() {
  clearInterval(state.quoteTimer);
  if (state.quotes.length <= 1) return;
  state.quoteTimer = setInterval(() => {
    state.quoteIndex = (state.quoteIndex + 1) % state.quotes.length;
    renderQuotes();
  }, 6000);
}

async function fetchAllContent() {
  try {
    const [products, videos, quotes] = await Promise.all([
      request("/products"),
      request("/videos"),
      request("/quotes"),
    ]);
    state.products = products;
    state.videos = videos;
    state.quotes = quotes;
    state.quoteIndex = 0;
    renderProducts();
    renderVideos();
    renderQuotes();
    startQuoteRotation();
  } catch (error) {
    console.error(error);
    showToast(`Unable to connect to the Atelier API: ${error.message}`, "error");
  }
}

function bindFormHandlers() {
  forms.product?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = {
      name: formData.get("name").trim(),
      description: formData.get("description").trim(),
      price: parseFloat(formData.get("price")),
      category: formData.get("category")?.trim() || null,
      image_url: formData.get("image_url")?.trim() || null,
      available: formData.get("available") === "on",
    };

    try {
      const product = await request("/products", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      state.products = [product, ...state.products];
      renderProducts();
      event.target.reset();
      event.target.querySelector("[name=available]").checked = true;
      showToast("Product added to your boutique!", "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  forms.video?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const productIdValue = formData.get("product_id");
    const payload = {
      title: formData.get("title").trim(),
      url: formData.get("url").trim(),
      description: formData.get("description")?.trim() || null,
      product_id: productIdValue ? Number(productIdValue) : null,
    };

    try {
      const video = await request("/videos", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      state.videos = [video, ...state.videos];
      renderVideos();
      event.target.reset();
      showToast("Video spotlight added!", "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  });

  forms.quote?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = {
      text: formData.get("text").trim(),
      author: formData.get("author")?.trim() || null,
    };

    try {
      const quote = await request("/quotes", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      state.quotes = [quote, ...state.quotes];
      state.quoteIndex = 0;
      renderQuotes();
      startQuoteRotation();
      event.target.reset();
      showToast("Quote added to your philosophy!", "success");
    } catch (error) {
      showToast(error.message, "error");
    }
  });
}

function bindUiNavigation() {
  buttons.prevQuote?.addEventListener("click", () => {
    if (!state.quotes.length) return;
    state.quoteIndex = (state.quoteIndex - 1 + state.quotes.length) % state.quotes.length;
    renderQuotes();
    startQuoteRotation();
  });

  buttons.nextQuote?.addEventListener("click", () => {
    if (!state.quotes.length) return;
    state.quoteIndex = (state.quoteIndex + 1) % state.quotes.length;
    renderQuotes();
    startQuoteRotation();
  });

  buttons.exploreCollection?.addEventListener("click", () => {
    document.querySelector("#products")?.scrollIntoView({ behavior: "smooth" });
  });

  buttons.watchKitchen?.addEventListener("click", () => {
    document.querySelector("#videos")?.scrollIntoView({ behavior: "smooth" });
  });

  buttons.ctaButton?.addEventListener("click", () => {
    showToast("Tasting reservations are opening soon!", "info");
  });
}

function setFooterYear() {
  const yearEl = document.querySelector("#year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
}

function init() {
  bindFormHandlers();
  bindUiNavigation();
  setFooterYear();
  fetchAllContent();
}

document.addEventListener("DOMContentLoaded", init);
