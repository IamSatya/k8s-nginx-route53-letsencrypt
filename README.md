# Kubernetes NGINX + Route53 + Let's Encrypt Operator

This repository includes everything you need to:

- Build and run a Docker-based Kubernetes Operator
- Deploy it with Helm to a local Kubernetes cluster
- Automatically configure virtual hosts on an external NGINX server
- Generate and renew TLS certificates with Let's Encrypt
- Manage DNS A-records via AWS Route53

---

# FLOW OF THE REQUEST
                ┌────────────────────┐
                │     Internet       │
                └────────┬───────────┘
                         ↓
            ┌──────────────────────────┐
            │ Firewall (Public IP)     │
            │ Port Forward: 80, 443    │
            └────────┬─────────────────┘
                     ↓
        ┌──────────────────────────────────┐
        │NGINX Reverse Proxy (Internal VM) │
        │ - Listens on 80, 443             │
        │ - Forwards to K8s Services       │
        └────────────┬─────────────────────┘
                     ↓
        ┌───────────────────────────────┐
        │ Kubernetes Cluster (Internal) │
        │ ┌───────────────────────────┐ │
        │ │  Service A (NodePort)     │ │
        │ │  Service B (ClusterIP)    │ │
        │ └───────────────────────────┘ │
        └───────────────────────────────┘


## 📦 Project Structure

```
nginx-operator/
├── Dockerfile
├── operator/
│   ├── __init__.py
│   └── controller.py
├── helm-chart/
│   ├── Chart.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── secrets.yaml
│   │   └── ...
│   └── values.yaml
└── README.md
```

---

## 🐳 Docker Image

```bash
docker build -t nginx-operator:latest .
```

If using kind:
```bash
kind load docker-image nginx-operator:latest
```

---

## 🔐 AWS Credentials Setup

Create a credentials file:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = YOUR_REGION
```

Create Kubernetes secret:
```bash
kubectl create secret generic aws-credentials \
  --from-file=credentials=aws-credentials \
  --namespace=default
```

---

## 🔑 SSH Key for Remote NGINX Server

```bash
kubectl create secret generic nginx-ssh-key \
  --from-file=id_rsa=/path/to/private/key \
  --namespace=default
```

---

## ⚙️ Helm Installation

```bash
helm install nginx-operator ./helm-chart \
  --set image.repository=nginx-operator \
  --set image.tag=latest \
  --set aws.region=us-east-1 \
  --set aws.hostedZoneId=Z123456ABCDEFG \
  --set nginx.host=192.168.1.10
```

---

## ✏️ Sample values.yaml

```yaml
aws:
  region: us-east-1
  hostedZoneId: Z123456ABCDEFG
  credentialsSecret: aws-credentials

nginx:
  host: 192.168.1.10
  sshKeySecret: nginx-ssh-key
  sshUser: ubuntu

image:
  repository: nginx-operator
  tag: latest
```

---

## 🌐 Service Annotations Example

Apply these annotations to any Kubernetes Service to auto-generate an NGINX vhost, TLS cert, and Route53 A-record:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-app
  annotations:
    nginx.domain: "app.example.com"
    nginx.nodePort: "32080"
spec:
  type: NodePort
  selector:
    app: example-app
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 32080
```

---

## 🔒 Let's Encrypt Support

The operator will:

- Auto-generate certs using certbot (DNS-01 challenge via Route53)
- Upload `.crt` and `.key` to `/etc/nginx/ssl/<domain>/` on the remote NGINX server
- Configure NGINX virtual host for HTTPS
- Reload NGINX
- Handle auto-renewal via scheduled checks

---

## ✅ Result

Once deployed, visiting `https://app.example.com` will:
- Resolve via AWS Route53
- Route through the external NGINX server to the internal Kubernetes NodePort
- Serve traffic over TLS with a valid Let's Encrypt cert

---

Maintained by [IamSatya](https://github.com/IamSatya).

