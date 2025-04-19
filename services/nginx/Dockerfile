FROM nginx:stable-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates
COPY ssl /etc/nginx/ssl

# Expose HTTP & HTTPS
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]