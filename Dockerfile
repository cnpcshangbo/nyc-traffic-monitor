# Node.js image for Vite development server
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (for better caching)
COPY package.json package-lock.json ./
RUN npm ci && \
    npm cache clean --force

# Copy only necessary application files (excluding those in .dockerignore)
COPY index.html vite.config.ts tsconfig*.json ./
COPY src ./src

# Create public directory structure (videos will be mounted as volumes)
RUN mkdir -p public/74th-Amsterdam-Columbus \
    public/Amsterdam-80th \
    public/Columbus-86th

# Copy static public files if they exist
COPY public/vite.svg public/vite.svg
COPY public/*.html public/

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server with host binding for Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]