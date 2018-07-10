FROM alpine:3.4
ENV NGINX_VERSION 1.13.6

COPY install.sh /usr/src/
COPY nginx.key /usr/src/

RUN sh -x /usr/src/install.sh

COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx.vh.default.conf /etc/nginx/conf.d/default.conf

# Create hashed temporary upload locations
RUN mkdir -p /tmp/0 /tmp/1 /tmp/2 /tmp/3 /tmp/4 /tmp/5 /tmp/6 /tmp/7 /tmp/8 /tmp/9

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
