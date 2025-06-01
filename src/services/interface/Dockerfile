# Build Stage
FROM node:18-alpine AS build-stage

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json* ./

# Install dependencies (including new shadcn/ui deps)
RUN npm install

# Copy configuration files
COPY tailwind.config.js postcss.config.js components.json ./

# Copy the rest of the application source code
COPY . .

# Build the React application
RUN npm run build

# Serve Stage
FROM nginx:stable-alpine

# Copy the build output from the build stage
COPY --from=build-stage /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
