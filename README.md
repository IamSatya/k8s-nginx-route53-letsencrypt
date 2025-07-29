# NGINX Operator for Kubernetes (Local Cluster)

## Docker Image

Build the image locally:

```bash
docker build -t nginx-operator .
```

## AWS Credentials

Create a Kubernetes secret `aws-credentials` with the following:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
```

## SSH Key

Create a secret `nginx-ssh-key` with your private key to access NGINX server:

```bash
kubectl create secret generic nginx-ssh-key --from-file=id_rsa
```
