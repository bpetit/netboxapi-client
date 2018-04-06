FROM python:2.7.14-alpine3.6

# Python Updated
RUN echo '* Installing OS dependencies' \
  && apk add --update --no-cache build-base \
  && echo '* Upgrade PIP' \
  && pip install --upgrade pip

# Global App behavior
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/netboxapi-client"]
CMD ["--help"]

# Preinstall App base
#COPY ./app/requirements.txt ./requirements.txt
#RUN echo '* Install App requirements' \
#  && pip install -r requirements.txt

# Add Code and update
COPY ./ ./
RUN echo '* Installing Python dependencies' \
  && python setup.py build \
  && pip install -e . \
  && echo '* Removing unneeded OS packages' \
  && apk del build-base
