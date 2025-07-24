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

# NGINX Operator with NodePort, TLS, and Route53 Support

This Kubernetes Operator automates:
- Detection of `Service` objects with a specific annotation (`nginx-operator.io/hostname`)
- TLS certificate provisioning via Let's Encrypt (using Certbot on a remote NGINX server)
- Automatic NGINX virtual host generation and reload
- A-record creation in AWS Route53

---

## 🧰 Prerequisites

- Kubernetes Cluster with Helm
- A running NGINX server accessible via SSH (outside the K8s cluster)
- A registered domain hosted in AWS Route53
- DNS pointing to public IP of your NGINX server (e.g. via Elastic IP or NAT)
- Certbot installed on the external NGINX server

---

## 📁 Helm Installation

```bash
helm upgrade --install nginx-operator ./helm/nginx-operator \
  -f custom-values.yaml
```

---

## ⚙️ Custom `values.yaml` Configuration

```yaml
replicaCount: 1

image:
  repository: nginx-operator
  tag: latest
  pullPolicy: IfNotPresent

nginxServer:
  host: 192.168.1.10         # External NGINX IP
  sshUser: ubuntu            # SSH user on NGINX server
  sshKeySecret: nginx-ssh    # K8s Secret name containing SSH private key

tls:
  email: admin@example.com   # Let's Encrypt registration email
  staging: true              # Set to false to use production certs

route53:
  enabled: true
  hostedZoneId: Z01234567890EXAMPLE
  domainSuffix: example.com
  region: us-east-1
  credentialsSecret: route53-creds
```

---

## 🔐 Create Required Secrets

### 1. SSH Private Key Secret
This SSH key must match the `authorized_keys` on your remote NGINX server.
```bash
kubectl create secret generic nginx-ssh \
  --from-file=id_rsa=~/.ssh/id_rsa
```

### 2. AWS Route53 Access Secret
Use IAM credentials with `route53:ChangeResourceRecordSets` and `route53:ListHostedZones` permissions.
```bash
kubectl create secret generic route53-creds \
  --from-literal=AWS_ACCESS_KEY_ID=AKIA... \
  --from-literal=AWS_SECRET_ACCESS_KEY=...
```

---

## 🚀 Usage

Annotate any service with `nginx-operator.io/hostname`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  annotations:
    nginx-operator.io/hostname: app.example.com
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  selector:
    app: my-app
```

The operator will:
- Detect the annotation
- Find a reachable node IP and nodePort
- Generate a virtual host file on remote NGINX
- Request a TLS cert using Certbot
- Reload NGINX
- Register an A-record in Route53

---

## 🔐 Let's Encrypt Certificate Generation (via Certbot)

The operator SSHs into the NGINX server and runs the following steps:

### 1. Check for existing cert:
```bash
sudo certbot certificates --domain app.example.com
```

### 2. If not found, generate using Certbot:
```bash
sudo certbot certonly \
  --nginx \
  --non-interactive \
  --agree-tos \
  --email admin@example.com \
  -d app.example.com
```

### 3. Manually reload NGINX:
```bash
sudo systemctl reload nginx
```

### 4. NGINX config sample generated:
```nginx
server {
    listen 443 ssl;
    server_name app.example.com;

    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    location / {
        proxy_pass http://<node-ip>:<node-port>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Auto-renewal setup
Certbot installs a systemd timer or cron job by default:
```bash
sudo certbot renew --quiet
```

You can verify with:
```bash
systemctl list-timers | grep certbot
```

---

## 🛠 TODO / Roadmap
- cert-manager support
- HTTP01 challenge fallback
- Multi-domain SAN cert support

---

For questions or contributions, please open a GitHub issue or PR.
