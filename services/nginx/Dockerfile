FROM nginx:stable-alpine

# remove the default vhost
RUN rm /etc/nginx/conf.d/default.conf

# copy your custom nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# expose only port 80
EXPOSE 80

# start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]