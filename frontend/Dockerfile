# syntax=docker/dockerfile:1

# Single-stage Dockerfile for Local Development

# Use a suitable Node.js base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Use 'ci' for potentially faster and more reliable installs in CI/CD,
# but 'install' is generally fine for local dev images.
RUN npm install

# Copy the rest of the frontend application code
# This will be overwritten by the volume mount in docker-compose.yml for local dev,
# but ensures the image has the code if run standalone.
COPY . .

# Expose the port Vite runs on (default is 5173)
EXPOSE 5173

# Default command to run the Vite development server
# This will be overridden by the command in docker-compose.yml, but serves as a default.
CMD ["npm", "run", "dev", "--", "--host"]