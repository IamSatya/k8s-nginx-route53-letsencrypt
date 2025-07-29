import os
import time
import base64
import boto3
import paramiko
import subprocess
from kubernetes import client, config, watch

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")
NGINX_HOST = os.getenv("NGINX_HOST")
NGINX_USER = os.getenv("NGINX_USER", "ubuntu")
NGINX_SSH_KEY_PATH = os.getenv("NGINX_SSH_KEY_PATH", "/root/.ssh/nginx.key")

def create_dns_record(fqdn, ip):
    route53 = boto3.client('route53', region_name=AWS_REGION)
    route53.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            "Comment": "Auto-created by nginx-operator",
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": fqdn,
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": ip}]
                }
            }]
        }
    )

def setup_tls(fqdn):
    subprocess.run([
        "certbot", "certonly", "--standalone",
        "-d", fqdn, "--non-interactive",
        "--agree-tos", "--register-unsafely-without-email"
    ], check=True)

def deploy_nginx_config(fqdn, port):
    config_block = f"""
server {{
    listen 443 ssl;
    server_name {fqdn};

    ssl_certificate /etc/letsencrypt/live/{fqdn}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{fqdn}/privkey.pem;

    location / {{
        proxy_pass http://127.0.0.1:{port};
    }}
}}
"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NGINX_HOST, username=NGINX_USER, key_filename=NGINX_SSH_KEY_PATH)

    remote_path = f"/etc/nginx/sites-available/{fqdn}.conf"
    symlink_path = f"/etc/nginx/sites-enabled/{fqdn}.conf"

    with ssh.open_sftp() as sftp:
        with sftp.file(remote_path, 'w') as f:
            f.write(config_block)
        sftp.chmod(remote_path, 0o644)

    ssh.exec_command(f"ln -sf {remote_path} {symlink_path}")
    ssh.exec_command("nginx -s reload")
    ssh.close()

def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    for event in w.stream(v1.list_service_for_all_namespaces):
        svc = event['object']
        annotations = svc.metadata.annotations or {}
        fqdn = annotations.get("nginx.fqdn")
        port = annotations.get("nginx.nodePort")

        if not fqdn or not port:
            continue

        external_ip = os.getenv("NGINX_PUBLIC_IP")
        if not external_ip:
            continue

        create_dns_record(fqdn, external_ip)
        setup_tls(fqdn)
        deploy_nginx_config(fqdn, port)

if __name__ == "__main__":
    main()
# logic for watching services and handling updates
