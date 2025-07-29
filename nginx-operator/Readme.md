# Kubernetes NGINX + Route53 + Let's Encrypt Operator

This operator watches Kubernetes services with specific annotations and automatically:

- Creates NGINX virtual host configurations on a remote NGINX server (192.168.1.10)
- Issues TLS certificates using Let's Encrypt
- Creates corresponding A records in AWS Route53

---

## 🛠 Prerequisites

- Kubernetes cluster (on-prem or cloud)
- NGINX server accessible via SSH (e.g., 192.168.1.10)
- AWS IAM user with Route53 permissions
- Helm installed

---

## 🔧 Helm Installation

### 1. Clone the Repository

```bash
git clone https://github.com/IamSatya/k8s-nginx-route53-letsencrypt.git
cd k8s-nginx-route53-letsencrypt
```

### 2. Create AWS Credentials Secret

Create a file named `aws-credentials` with your AWS credentials:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = YOUR_REGION
```

Then create a Kubernetes secret:

```bash
kubectl create secret generic aws-credentials \
  --from-file=credentials=aws-credentials \
  --namespace=default
```

### 3. Add SSH Key Secret (for remote NGINX access)

```bash
kubectl create secret generic nginx-ssh-key \
  --from-file=id_rsa=/path/to/your/private_key \
  --namespace=default
```

### 4. Update `values.yaml`

Edit these values in `values.yaml`:

```yaml
aws:
  credentialsSecret: aws-credentials
  hostedZoneId: YOUR_HOSTED_ZONE_ID
  region: YOUR_REGION

nginx:
  host: 192.168.1.10
  user: ubuntu
  sshKeySecret: nginx-ssh-key

certbot:
  email: your-email@example.com
```

### 5. Install via Helm

```bash
helm install nginx-operator ./chart
```

---

## 📝 Service Annotation Example

Add annotations to your Kubernetes service like this:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-app
  annotations:
    nginx-operator/enabled: "true"
    nginx-operator/hostname: "app.example.com"
    nginx-operator/cert-type: "letsencrypt"
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: example
```

---

## 🔁 Auto-Renew & Cleanup

- Let's Encrypt certificates are auto-renewed using `certbot renew` via a background cron job.
- Removed services are automatically cleaned from NGINX and Route53.

---

## 🐳 Docker Image

To build the image:

```bash
docker build -t nginx-operator:latest .
```

For local cluster testing:

```bash
kind load docker-image nginx-operator:latest
```

---

## 📂 File Structure

```
k8s-nginx-route53-letsencrypt/
├── chart/                   # Helm chart
├── nginx_operator/         # Operator source code
│   ├── __init__.py
│   ├── watcher.py
│   ├── certbot.py
│   └── dns.py
├── Dockerfile
├── values.yaml             # Helm values file
├── requirements.txt
└── README.md
```

---

## 📬 Contact

Maintained by [IamSatya](https://github.com/IamSatya). Contributions welcome!
