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

############################
# Production stage
############################
FROM nginx:alpine AS prod

# Copy built static files to nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]