FROM alpine:3.7

WORKDIR /app

COPY . /app

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    sqlite \
    build-base \
  && rm -rf /var/cache/apk/*

RUN pip install --trusted-host pypi.python.org -r requirement.txt

EXPOSE 80

ENV NAME World

ENV TEAM_ID=CC_070_077_207_490

CMD ['python','run.py']
