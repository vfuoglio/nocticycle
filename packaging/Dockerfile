# Optional: build inside an older base image so the binary runs on older distros (glibc 2.31+).
# Needs a running Docker daemon.
#   docker build -t nocticycle-build -f packaging/Dockerfile packaging
#   docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/src nocticycle-build
FROM python:3.11-bullseye
# Debian 11 is EOL (its package repos are gone), so rely on the tools the base image ships.
RUN which curl objdump file
RUN pip install --no-cache-dir pyinstaller skyfield tzdata geopy timezonefinder certifi
WORKDIR /src
CMD ["packaging/build.sh"]
