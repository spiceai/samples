FROM debian as build

RUN apt-get update && apt-get install -yqq curl jq

RUN curl https://install.spiceai.org/install-spiced.sh | /bin/bash

FROM debian

RUN apt-get update && apt-get install -yqq libssl-dev

COPY --from=build /usr/local/bin/spiced /usr/local/bin

WORKDIR /root

ENTRYPOINT ["spiced", "--flight", "0.0.0.0:50051"]