FROM debian:stable

ENV HOME=/root

RUN \
  apt-get update && \
  apt-get -y full-upgrade --auto-remove && \
  apt-get -y install --no-install-recommends \
    ca-certificates \
    git make pkg-config gcc \
    python3-dev python3-setuptools python3-pip python3-wheel \
    rsyslog \
    && \
  apt-get clean && \
  update-rc.d rsyslog enable
