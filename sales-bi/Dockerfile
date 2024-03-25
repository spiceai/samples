FROM rust as build

RUN apt-get update && apt-get install -yqq git

ARG cache=true2

RUN git clone https://github.com/spiceai/spiceai.git && \
    cd spiceai && \
    git checkout phillip/240325-fix-null-value-load

RUN cd spiceai && make -C bin/spiced

FROM debian

RUN apt-get update && apt-get install -yqq libssl-dev sqlite3

COPY --from=build /spiceai/target/release/spiced /usr/local/bin

WORKDIR /root

ENTRYPOINT ["spiced", "--flight", "0.0.0.0:50051"]