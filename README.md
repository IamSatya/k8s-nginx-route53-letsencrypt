## NGINX Operator for Kubernetes with Route53 + Let's Encrypt

This operator watches Kubernetes services annotated with virtual host and DNS info, then:
- Creates an NGINX virtual host config on a remote server (via SSH)
- Requests TLS certs from Let's Encrypt
- Creates a Route53 A record pointing to the public IP of the NGINX server

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

## 🛠️ Prerequisites

- Kubernetes cluster (minikube, kind, bare metal, etc.)
- External NGINX server accessible via SSH (e.g., 192.168.1.10)
- AWS Route53 hosted zone

---

## 🔧 Setup & Installation

### Step 1: Build Docker Image
```bash
docker build -t nginx-operator .
```

### Step 2: Push Image to Registry (if not running locally)
```bash
docker tag nginx-operator <your-registry>/nginx-operator
```

### Step 3: Add Helm Secrets

```bash
kubectl create secret generic aws-credentials \
  --from-literal=credentials='[default]\naws_access_key_id=YOUR_KEY\naws_secret_access_key=YOUR_SECRET\nregion=us-east-1'

kubectl create secret generic nginx-ssh-key \
  --from-file=id_rsa=/path/to/private_key
```

### Step 4: Install Helm Chart
```bash
cd helm-chart
helm install nginx-operator . \
  --set image.repository=nginx-operator \
  --set image.tag=latest \
  --set aws.hostedZoneId=YOUR_ZONE_ID \
  --set ssh.host=192.168.1.10 \
  --set ssh.user=ubuntu
```

---

## 🧪 Usage Example (Kubernetes Service)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  annotations:
    nginx.host: myapp.example.com
    nginx.port: "8080"
    nginx.letsencrypt: "true"
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 30080
```

---

## 🔒 Let's Encrypt Integration

When `nginx.letsencrypt: "true"` is present in a service annotation:
- The operator triggers `certbot` on the NGINX host using HTTP-01 challenge
- Certs are stored and mounted into the vhost config
- Auto-renewal is handled via cron job in the container

---

## 🧹 Cleanup

When a service is deleted, the operator will:
- Remove NGINX vhost config on remote server
- Remove Route53 A record
- Remove certs (optional)

---

## 📁 Repo Layout
- `operator/`: Python source code for controller, Route53, NGINX, certbot
- `helm-chart/`: Deployable Helm chart for operator
- `Dockerfile`: Containerizes the operator

---
