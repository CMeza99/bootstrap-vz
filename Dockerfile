FROM ubuntu:16.04

ENV INITRD=No \
    debian_frontend=noninteractive \
    LC_ALL=C.UTF-8 \
    unicode=YES

COPY setup.py /opt/bootstrap-vz/
COPY bootstrapvz/ /opt/bootstrap-vz/bootstrapvz/
COPY run-bootstrapvz.sh /usr/local/bin/bootstrap-vz.sh

RUN cd && set -ex && \
  echo 'Acquire::http {No-Cache=True;};' | tee /etc/apt/apt.conf.d/no-http-cache && \
  dpkg-divert --local --rename --add /usr/bin/ischroot && \
    ln -sf /bin/true /usr/bin/ischroot && \
  apt-get update && \
  apt-get install -y --no-install-recommends apt-transport-https ca-certificates && \
  apt-get dist-upgrade -y --no-install-recommends -o Dpkg::Options::="--force-confold" && \
  apt-get install -y --no-install-recommends wget && \
  echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(grep DISTRIB_CODENAME /etc/lsb-release | cut -d= -f2) stable" > /etc/apt/sources.list.d/docker-ce.list && \
  wget --https-only --no-cookies --no-hsts --no-cache --quiet --output-document - https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
  apt-get update && \
  apt-get install -y --no-install-recommends python debootstrap parted kpartx docker-ce aufs-tools && \
  wget --https-only --no-cache --no-hsts --no-verbose https://github.com/krallin/tini/releases/download/v0.16.1/tini_0.16.1-amd64.deb && \
  wget --https-only --no-cache --no-hsts --no-verbose https://github.com/krallin/tini/releases/download/v0.16.1/tini_0.16.1-amd64.deb.asc && \
  gpg --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 && \
  gpg --verify tini_0.16.1-amd64.deb.asc && \
  dpkg -i tini_0.16.1-amd64.deb && \
  rm -f -- tini_0.16.1-amd64.deb.asc tini_0.16.1-amd64.deb && \
  wget --https-only --no-cookies --no-hsts --no-cache --no-verbose --output-document=/usr/local/bin/dind https://raw.githubusercontent.com/moby/moby/master/hack/dind && \
  chmod +x /usr/local/bin/dind && \
  wget --https-only --no-cookies --no-hsts --no-cache --no-verbose https://bootstrap.pypa.io/get-pip.py && \
  python get-pip.py && rm -f get-pip.py && \
  pip --no-cache-dir install --upgrade /opt/bootstrap-vz/ awscli && \
  pip uninstall -y pip && \
  apt-get purge -y wget apt-transport-https && \
  apt-get autoremove -y && \
  apt-get clean && \
  rm -rf -- /tmp/* /var/tmp/* \
     /var/cache/apt/* /var/lib/apt/lists/* \
     /root/.gnupg

# ENTRYPOINT ['/usr/local/bin/bootstrap-vz.sh']
# CMD ['--help']

ENTRYPOINT ["/usr/bin/tini", "-g", "--"]
