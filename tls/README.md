# Secure communication with TLS

This sample will guide you through the steps required to set up secure communication using TLS using the Spice.ai runtime. We will cover the creation of a Certificate Authority (CA), generating a certificate signing request (CSR) and private key, signing the CSR with the CA, and running Spice with TLS.

# Requirements
- OpenSSL
  - macOS: `brew install openssl`
  - Ubuntu: `sudo apt-get install openssl`
  - Windows: [Download OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)
- Spice.ai runtime
  - [Install Spice.ai](https://docs.spiceai.org/installation)

# Navigate to the `tls` directory

The rest of the commands in this tutorial should be run from the `tls` directory.

```bash
cd tls
```

# Create a CA

First, we need to create a CA. This involves generating a private key and a self-signed certificate for the CA.

```bash
# Generate a private key and self-signed certificate for the CA
openssl genpkey -algorithm RSA -out ca.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key ca.key -out ca.pem -days 3650 -config ca.cnf
```

# Create a certificate signing request & private key for `spiced`
Next, we'll create a private key and a CSR for the `spiced` service.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out spiced.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key spiced.key -out spiced.csr -config spiced.cnf
```

## Sign the CSR with the CA
Now, we'll sign the CSR with the CA to generate a certificate for the `spiced` service.
```bash
# Sign the CSR with the CA
openssl x509 -req -in spiced.csr -CA ca.pem -CAkey ca.key -out spiced.crt -days 365 -copy_extensions copy
```

# Create a certificate signing request & private key for `postgres`
Similar to `spiced` we'll create a private key and a CSR for the `postgres` instance.

```bash
# Generate a private key (ECDSA)
openssl ecparam -genkey -name prime256v1 -out postgres.key
# Generate a certificate signing request (CSR) for the private key
openssl req -new -key postgres.key -out postgres.csr -config postgres.cnf
```

## Sign the CSR with the CA
Now, we'll sign the CSR with the CA to generate a certificate for the `postgres` instance.
```bash
# Sign the CSR with the CA
openssl x509 -req -in postgres.csr -CA ca.pem -CAkey ca.key -out postgres.crt -days 365 -copy_extensions copy
```

# Run `spiced` with TLS

With the certificate and key generated, we can now run the `spiced` service with TLS enabled.

```bash
spiced --tls --tls-certificate-file ./spiced.crt --tls-key-file ./spiced.key
```

# Verify the TLS connection

```bash
curl --cacert ca.pem https://localhost:8090/health
```

If the connection is successful, you should see a response indicating that the service is up and running.

## Summary

In this tutorial, we've walked through the process of setting up TLS for secure communication. We created a CA, generated a CSR and private key for the `spiced` service, signed the CSR with the CA, ran the service with TLS, and verified the TLS connection. Following these steps ensures that your communication is encrypted and secure.

Feel free to reach out if you have any questions or need further assistance!
