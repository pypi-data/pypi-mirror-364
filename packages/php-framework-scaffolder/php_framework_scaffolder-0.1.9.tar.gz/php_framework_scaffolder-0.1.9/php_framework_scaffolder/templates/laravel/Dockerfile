FROM php:{{ php_version }}-alpine

{% for package in apk_packages %}
RUN apk add --no-cache {{ package }}
{% endfor %}

{% for extension in php_extensions %}
RUN docker-php-ext-install {{ extension }}
{% endfor %}

{% for extension in pecl_extensions %}
RUN pecl install {{ extension }}
RUN docker-php-ext-enable {{ extension }}
{% endfor %}

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer
RUN echo 'memory_limit = 2G' > /usr/local/etc/php/conf.d/docker-php-memlimit.ini
RUN composer global require zircote/swagger-php

COPY ./src /app/

RUN if [ -f /app/.env.example ]; then cp /app/.env.example /app/.env; else echo "APP_KEY=base64:$(openssl rand -base64 32)" >> /app/.env; fi
WORKDIR /app
RUN composer install

WORKDIR /app/public
ENTRYPOINT [ "php", "-S", "0.0.0.0:80" ]