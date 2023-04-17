FROM node:current-alpine AS build

WORKDIR /usr/src/demo-web-app-frontend

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /usr/src/demo-web-app-frontend/www /usr/share/nginx/html
COPY docker/default.conf /etc/nginx/conf.d/default.conf

