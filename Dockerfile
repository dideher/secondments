FROM python:3.10-alpine AS compile-image
ARG ENVIRONMENT=development

## update alpine and install build deps
RUN set -x \
    apk update \
    && apk add --no-cache \
        gcc \
        libc-dev \
        linux-headers \
        jpeg-dev \
        zlib-dev \
        libjpeg  \
        musl-dev \
        mariadb-connector-c-dev
        #mariadb-dev
        #mariadb-client
        #postgresql-dev


## virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

## install requirements
RUN set -x \
    && pip install --upgrade pip wheel pip-tools

COPY requirements.txt ./requirements.in
COPY requirements-local.txt ./requirements-local.txt


RUN set -x \
    && pip-compile ./requirements.in > ./requirements.txt \
    && pip-sync \
    && pip install -r ./requirements.txt


FROM python:3.10-alpine AS runtime-image
ARG ENVIRONMENT=development

# partially inspired from https://github.com/tiangolo/meinheld-gunicorn-docker

## update alpine and install runtime deps
RUN set -x \
    apk update \
    && apk add --virtual \
        libjpeg-turbo \
        zlib \
        libjpeg \
        openssl \
        ca-certificates \
        mariadb-connector-c \
        mariadb-client \
        nginx \
        vim

## copy Python dependencies from build image
COPY --from=compile-image /opt/venv /opt/venv

## prepare nginx
COPY docker-files/nginx.conf /etc/nginx/http.d/default.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY docker-files/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY docker-files/start.sh /start.sh
RUN chmod +x /start.sh

COPY docker-files/prestart.sh /prestart.sh
RUN chmod +x /prestart.sh

COPY docker-files/gunicorn_conf.py /gunicorn_conf.py

COPY ./app /app
WORKDIR /app/


ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Meinheld
CMD ["/start.sh"]