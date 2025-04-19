# syntax=docker/dockerfile:1

############################
# Build stage
############################
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Dev stage
# <-- Updated Node version
FROM node:20-alpine AS dev

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]

############################
# Production stage
############################
FROM nginx:stable-alpine AS prod

# Copy built static files to nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Explicitly run as the non-root nginx user
USER nginx

CMD ["nginx", "-g", "daemon off;"]