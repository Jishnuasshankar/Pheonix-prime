# ==============================================================================
# MasterX Frontend - Production-Ready Multi-Stage Dockerfile
# ==============================================================================
# Following Big Tech Standards: Google/Meta/Amazon
# - Multi-stage builds (builder + nginx serve)
# - Layer caching optimization
# - Minimal production image with nginx
# - Security hardening
# - Optimized static asset delivery
# ==============================================================================

# ==============================================================================
# STAGE 1: Builder - Build React application
# ==============================================================================
FROM node:20-alpine as builder

LABEL maintainer="MasterX Team"
LABEL description="MasterX Frontend - Builder Stage"

# Set working directory
WORKDIR /app

# Copy package files first for better layer caching
# This layer is cached unless package.json or yarn.lock changes
COPY package.json yarn.lock ./

# Install dependencies with frozen lockfile (ensures reproducible builds)
RUN yarn install --frozen-lockfile --production=false

# Copy source code
COPY . .

# Build application for production
# This creates optimized static files in /app/dist
RUN yarn build

# ==============================================================================
# STAGE 2: Production - Serve with Nginx
# ==============================================================================
FROM nginx:alpine

LABEL maintainer="MasterX Team"
LABEL description="MasterX Frontend - Production Runtime"
LABEL version="1.0.0"

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx user (if not exists) and set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
