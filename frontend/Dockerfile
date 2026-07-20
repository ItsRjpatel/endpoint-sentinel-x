# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:1.25-alpine

COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom Nginx configuration if needed, or rely on defaults
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
