# ------------ React Build Stage -------------
FROM node:18-alpine AS build-stage

WORKDIR /app

# Install dependencies
COPY package.json /app/package.json
RUN npm install

# Copy rest of frontend code
COPY public /app/public
COPY src /app/src

# Build React for production
RUN npm run build


# ------------ Nginx Serve Stage -------------
FROM nginx:stable-alpine

# Copy build output into nginx html folder
COPY --from=build-stage /app/build /usr/share/nginx/html

# Replace default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
