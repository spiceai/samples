# Encryption in transit using TLS

This sample demonstrates configuring Spice for encryption in transit using TLS and includes a sample client application that connects to the runtime securely. The Spice runtime is configured to use TLS for remote connections and to require TLS for its own HTTP and gRPC endpoints.

First a CA (Certificate Authority) will be created with OpenSSL. Then, certificates will be generated for the `spiced` service and a `postgres` instance and signed by the CA. `postgres` & `spiced` will be started with TLS enabled. The `spicepod.yaml` included in this sample will connect securely to `postgres`. Finally, the TLS connection will be verified using cURL and running a small Go application that connects and does a simple query to the `spiced` service.

# Requirements

- OpenSSL
  - macOS: `brew install openssl`
  - Ubuntu: `sudo apt-get install openssl`
  - Windows: [Download OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)
- Spice.ai runtime
  - [Install Spice.ai](https://docs.spiceai.org/installation)
- cURL
- Docker
- Go (optional, for building the sample application)

# Navigate to the `tls` directory

The rest of the commands in this tutorial should be run from the `tls` directory.

```bash
cd tls
```

# Create a CA (Certificate Authority)

First, create a CA. This involves generating a private key and a self-signed certificate.

```bash
# Generate a private key and self-signed certificate for the CA
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key ca.key -out ca.pem -days 3650 -config ca.cnf
```

# Create a certificate signing request & private key for `spiced`

Next, create a private key and a CSR (Certificate Signing Request) for `spiced`.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out spiced.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key spiced.key -out spiced.csr -config spiced.cnf
```

## Sign the CSR with the CA

Sign the CSR with the CA to generate a certificate for `spiced`.

```bash
# Sign the CSR with the CA
openssl x509 -req -in spiced.csr -CA ca.pem -CAkey ca.key -out spiced.crt -days 365 -copy_extensions copy
```

# Create a certificate signing request & private key for `postgres`

Similar to `spiced` create a private key and a CSR for `postgres`.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out postgres.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key postgres.key -out postgres.csr -config postgres.cnf
```

## Sign the CSR with the CA

Sign the CSR with the CA to generate a certificate for `postgres`.

```bash
# Sign the CSR with the CA
openssl x509 -req -in postgres.csr -CA ca.pem -CAkey ca.key -out postgres.crt -days 365 -copy_extensions copy
```

# Start `postgres` with TLS

## Ubuntu: Change key file owner and permissions

On Ubuntu, permissions changes are required to allow the `postgres` Docker instance to accesss the key.

Set the owner to the UID `999` and GID `999`, which [match the UID and GID of the `postgres` user.](https://github.com/docker-library/postgres/blob/master/17/bullseye/Dockerfile#L10-L13)

```bash
sudo chown 999:999 postgres.key
sudo chmod 600 postgres.key
```

## Start `postgres`

Start a `postgres` instance with TLS enabled using Docker compose.

```bash
docker compose up -d
```

# Run `spiced` with TLS

With the certificate and key generated, run the `spiced` service with TLS enabled.

```bash
spice run -- --tls-certificate-file ./spiced.crt --tls-key-file ./spiced.key
```

# Verify the TLS connection

In a separate terminal, verify the TLS connection using cURL.

```bash
curl --cacert ca.pem https://localhost:8090/health
```

# Build and run the sample Go application

The sample Go application connects securely to the `spiced` service over TLS and does a simple query using the `flightsql` ADBC driver.

```bash
cd tls # If not already in the tls directory
go run main.go
```

# Use `spice sql` to securely connect to the `spiced` service

```bash
spice sql --tls-root-certificate-file ./ca.pem
```

Run a simple query to verify the connection.

```sql
SELECT * FROM customer_addresses LIMIT 5;
```

# Clean up

```bash
rm ca.key ca.pem spiced.key spiced.csr spiced.crt postgres.key postgres.csr postgres.crt
docker compose down
```

# Summary

This sample covered how to configure the Spice runtime to connect to remote data sources securely using TLS, how to configure the Spice runtime to use TLS for its own endpoints, and how to create an application that connects to the runtime securely.
