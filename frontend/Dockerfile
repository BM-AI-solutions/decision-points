# syntax=docker/dockerfile:1

FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Set environment variables
ENV NODE_ENV=production
ENV VITE_API_TIMEOUT=30000

# Copy frontend source code
COPY . .

# Run the production build
RUN npm run build

# Use a smaller image for serving
FROM node:20-alpine

WORKDIR /app

# Install serve for production static file serving
RUN npm install -g serve

# Copy built assets from the build stage
COPY --from=build /app/dist /app/dist

# Expose port for serving the built application
EXPOSE 3000

# Serve the static files with optimized settings
CMD ["serve", "-s", "dist", "-l", "3000", "--no-clipboard", "--no-port-switching"]
