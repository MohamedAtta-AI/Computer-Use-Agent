# ──────────────────────────────────────────────────────────────────────────────
# Build stage – compiles the Vite / React UI
# ──────────────────────────────────────────────────────────────────────────────
FROM node:20-bullseye AS builder

# Create non-root user for reproducible builds
RUN useradd -m appuser
WORKDIR /home/appuser/app

# Copy package files first
COPY --chown=appuser:appuser package.json package-lock.json* ./

# Install dependencies and explicitly add the missing rollup native package
RUN npm ci --omit=dev --force && \
    npm install @rollup/rollup-linux-x64-gnu --platform=linux --arch=x64

# Copy source code
COPY --chown=appuser:appuser . .

# Build Vite production bundle
RUN npm run build

# ──────────────────────────────────────────────────────────────────────────────
# Runtime stage – ultra-small static file server
# ──────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Copy compiled assets
COPY --from=builder /home/appuser/app/dist /usr/share/nginx/html

# Slim default NGINX config → single-page app routing
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/spa.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
