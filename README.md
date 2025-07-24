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

## 🛠 TODO / Roadmap
- cert-manager support
- HTTP01 challenge fallback
- Multi-domain SAN cert support

---

For questions or contributions, please open a GitHub issue or PR.
