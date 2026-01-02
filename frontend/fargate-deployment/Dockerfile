# frontend/fargate-deployment/Dockerfile

# Step 1: Build React/Vite
FROM node:20-alpine AS build
WORKDIR /app
# Note: Paths are now relative to PROJECT ROOT
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Step 2: Nginx
FROM nginx:alpine
# Copy the build output from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html
# Copy your template
COPY frontend/fargate-deployment/nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
