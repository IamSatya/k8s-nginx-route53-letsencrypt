# Kubernetes NGINX + Route53 + Let's Encrypt Operator

This Helm chart deploys a Kubernetes operator that watches services with specific annotations and automatically:

- Creates NGINX virtual host configurations on a remote NGINX server (e.g. 192.168.1.10)
- Issues Let's Encrypt TLS certificates
- Creates A records in AWS Route53

---

## 🐳 Docker Image

Build the Docker image locally:

```bash
docker build -t nginx-operator:latest .
```

To use in local Kubernetes clusters (e.g., kind):

```bash
kind load docker-image nginx-operator:latest
```

If hosting on a public or private registry, push the image accordingly and update the Helm `values.yaml` to use it.

---

## 🔐 AWS Credentials Setup

Create a Kubernetes secret that includes your AWS credentials:

1. Create an AWS credentials file named `aws-credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = YOUR_REGION
```

2. Create the secret in Kubernetes:

```bash
kubectl create secret generic aws-credentials \
  --from-file=credentials=aws-credentials \
  --namespace=default
```

3. Reference this secret in your Helm `values.yaml`:

```yaml
aws:
  credentialsSecret: aws-credentials
  hostedZoneId: YOUR_HOSTED_ZONE_ID
  region: YOUR_REGION
```

---

For full usage instructions, see the repository documentation or values.yaml examples.

Maintained by [IamSatya](https://github.com/IamSatya).
