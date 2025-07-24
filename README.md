# NGINX TLS Operator

This operator watches for Kubernetes Services and:
- Creates virtual host configs for NGINX
- Adds Let's Encrypt TLS certs (auto-renew)
- Updates AWS Route53 A-record
- Removes all resources on deletion

## Features
- Remote NGINX config management over SSH
- Helm-deployable
- TLS + DNS auto handled
- Lightweight Python+Kopf

## Installation

```sh
helm install nginx-operator ./charts/nginx-operator
```

Make sure you create a Kubernetes secret with your SSH private key:

```sh
kubectl create secret generic nginx-ssh-key --from-file=id_rsa=/path/to/id_rsa
```

## Customize

Edit `values.yaml` to match:
- `nginx.host`, `user`, `sshKeyPath`
- `certbot.email`
- `aws.hostedZoneId`, `publicIp`

