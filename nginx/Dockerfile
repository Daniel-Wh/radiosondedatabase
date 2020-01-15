FROM tutum/nginx

RUN rm /etc/nginx/sites-enabled/default
COPY web.conf /etc/nginx/sites-available
RUN ln -s /etc/nginx/sites-available/web.conf /etc/nginx/sites-enabled/web.conf