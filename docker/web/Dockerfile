FROM nginx:1.27-alpine

COPY index.html /usr/share/nginx/html/index.html
COPY data /usr/share/nginx/html/data
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
