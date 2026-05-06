FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
RUN addgroup -S arkhe && adduser -S arkhe -G arkhe
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=frontend-builder /app/dist /usr/share/nginx/html
RUN chown -R arkhe:arkhe /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
