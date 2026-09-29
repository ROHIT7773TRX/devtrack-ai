# ============================================================
# app/frontend/Dockerfile
# Multi-stage Docker build for React Frontend
#
# STAGE 1: Build environment
# STAGE 2: Lightweight production Nginx web server
# ============================================================

# --- Stage 1: Build static assets ---
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile || npm install

COPY . .

# Set default API URL environment variable for production build
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

RUN npm run build

# --- Stage 2: Nginx Web Server ---
FROM nginx:alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static HTML/JS assets from Stage 1
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
