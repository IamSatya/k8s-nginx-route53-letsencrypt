# NGINX Operator with NodePort Support

This Kubernetes Operator watches services with annotations and:
- Requests Let's Encrypt TLS certs
- Creates NGINX configs
- Routes traffic using NodePort services and node IPs
- Pushes config to external NGINX (192.168.1.10)
- Sets up auto TLS renewal

## Annotated Service Example

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  annotations:
    nginx-operator.io/enabled: "true"
    nginx-operator.io/hostname: "app.example.com"
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

The operator finds a cluster node IP and configures:

```nginx
proxy_pass http://<node-ip>:30080;
```

## Install with Helm

```bash
helm install nginx-operator ./helm/nginx-operator
```