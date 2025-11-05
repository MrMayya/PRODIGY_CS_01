# RarePeti Atelier — Boutique Pet Cuisine Platform

An elegant, full-stack experience inspired by [RarePeti](https://rarepeti.com/). This project pairs a FastAPI backend with a vanilla JavaScript frontend so you can curate gourmet pet products, showcase preparation videos, and share inspiring quotes with your visitors.

<p align="center">
  <img src="https://images.unsplash.com/photo-1548943487-a2e4e43b4853" alt="Gourmet pet cuisine" width="420" />
</p>

## Features
- 🛍️ **Product Boutique**: Add, update, and showcase small-batch pet cuisine offerings.
- 🎥 **Video Atelier**: Embed preparation and behind-the-scenes clips (YouTube/Vimeo friendly).
- ✨ **Quote Carousel**: Rotate through meaningful brand statements to delight your audience.
- 🎨 **Luxury Frontend**: A refined, mobile-responsive design using pure HTML/CSS/JS.
- 🗃️ **SQLite Persistence**: Simple storage seeded with artisan sample content out of the box.

## Project Layout

```
rarepeti_clone/
├── backend/
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── data/                # SQLite database lives here (auto-created)
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── README.md
└── requirements.txt
```

## Prerequisites

- Python **3.11+**
- Node.js (optional, only if you prefer using a Node-based static server)

## 1. Local Backend Setup

```bash
cd rarepeti_clone
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Run the API (port 8000 by default)
uvicorn backend.main:app --reload
```

FastAPI automatically serves interactive API docs at <http://127.0.0.1:8000/docs>.

### Available Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/health` | Readiness health check |
| GET | `/api/products` | List products (videos expanded) |
| POST | `/api/products` | Create a product |
| PATCH | `/api/products/{id}` | Update a product |
| DELETE | `/api/products/{id}` | Remove a product |
| GET | `/api/videos` | List videos |
| POST | `/api/videos` | Create a video entry |
| GET | `/api/quotes` | List quotes |
| POST | `/api/quotes` | Create a quote |

> The first run seeds the database with sample products, videos, and quotes for quick demos.

## 2. Local Frontend Preview

The frontend is a static site that consumes the API. You can serve it in multiple ways:

```bash
# Option A: Python's built-in static server
cd rarepeti_clone/frontend
python -m http.server 5173

# Option B: Node-based server (if you have Node installed)
npx serve .
```

Visit <http://127.0.0.1:5173> (or whichever port your static server prints). The frontend expects the API at `http://localhost:8000/api` by default. To point to a different backend, inject a global config before `app.js` in `index.html`:

```html
<script>
  window.APP_CONFIG = { apiBase: "https://your-domain.example.com/api" };
</script>
<script type="module" src="app.js"></script>
```

## 3. Packaging for Deployment

### Create a production build (optional but recommended)

- Minify `frontend/` assets (e.g., via `terser`, `html-minifier`, or your preferred pipeline).
- Harden the backend `uvicorn` command (turn off `--reload`, use `--host 0.0.0.0 --port 8000`).

### Example systemd service for the API

```ini
[Unit]
Description=RarePeti Atelier API
After=network.target

[Service]
User=www-data
WorkingDirectory=/srv/rarepeti_clone
Environment="PATH=/srv/rarepeti_clone/.venv/bin"
ExecStart=/srv/rarepeti_clone/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 4. Deploying on Akamai Connected Cloud (former Linode)

> Akamai’s cloud platform provides traditional VMs (Compute Instances) along with load balancing, storage, and CDN options. The steps below outline a typical single-node deployment.

1. **Create a Compute Instance**
   - Log into <https://cloud.linode.com/>.
   - Choose a region close to your audience.
   - Select an Ubuntu 22.04 LTS image and a plan (Shared CPU is sufficient for prototypes).

2. **Secure the instance**
   - Add your SSH key during creation or upload afterward.
   - Disable password authentication (`/etc/ssh/sshd_config`) and enable a basic firewall (`ufw allow OpenSSH`).

3. **Install runtime dependencies**

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3.11 python3.11-venv nginx git
   ```

4. **Clone and configure the project**

   ```bash
   sudo mkdir -p /srv/rarepeti_clone
   sudo chown $USER:$USER /srv/rarepeti_clone
   git clone https://your.git.repo/rarepeti_clone.git /srv/rarepeti_clone
   cd /srv/rarepeti_clone
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run migrations / seed (automatic on first start)**
   - The FastAPI startup hook prepares the SQLite database at `data/app.db`.

6. **Configure a process manager**
   - Use the `systemd` unit above (copy to `/etc/systemd/system/rarepeti.service`).
   - Enable and start: `sudo systemctl enable --now rarepeti.service`.

7. **Serve the frontend and reverse proxy with Nginx**

   ```nginx
   server {
     listen 80;
     server_name your-domain.com;

     root /srv/rarepeti_clone/frontend;
     index index.html;

     location /api/ {
       proxy_pass http://127.0.0.1:8000/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
     }

     location / {
       try_files $uri $uri/ /index.html;
     }
   }
   ```

   - Test: `sudo nginx -t`
   - Reload: `sudo systemctl reload nginx`

8. **Add TLS (Let’s Encrypt)**
   - Install Certbot: `sudo snap install --classic certbot`
   - Run `sudo certbot --nginx -d your-domain.com`

9. **Scale with Akamai services (optional)**
   - Front everything with Akamai CDN for global caching.
   - Use Akamai Load Balancers or NodeBalancers to distribute across multiple compute instances.
   - Store product assets/videos in Akamai Object Storage (S3-compatible) if you upload media.

## 5. Operational Notes

- **Database**: SQLite is perfect for getting started. For multi-node scaling, migrate to PostgreSQL (Akamai Managed Databases) and update `DATABASE_URL` in `backend/database.py`.
- **Security**: Implement authentication/authorization before exposing admin forms publicly. FastAPI supports OAuth and API keys.
- **Backups**: Snapshot the VM or back up `data/app.db` regularly.
- **Monitoring**: Akamai offers Cloud Monitor. Alternatively, wire FastAPI metrics into Prometheus + Grafana.

## 6. Extending the Experience

- Add a shopping cart and checkout flow (Stripe, Square, etc.).
- Enable image uploads with Akamai Object Storage and signed URLs.
- Introduce localization and multi-currency pricing.
- Bring in analytics to understand customer behavior.

## Support

If you have questions or need enhancements (authentication, e-commerce integrations, or UI refinements), feel free to reach out. Enjoy crafting unforgettable culinary moments for your companions! 🐾

