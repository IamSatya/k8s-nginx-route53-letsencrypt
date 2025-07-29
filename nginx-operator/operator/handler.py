import kopf
import logging
import paramiko
import boto3
import os

@kopf.on.create('v1', 'Service')
def on_service_create(body, spec, name, namespace, **kwargs):
    annotations = body['metadata'].get('annotations', {})
    host = annotations.get("nginx.host")
    port = annotations.get("nginx.port")
    tls = annotations.get("nginx.tls", "false").lower() == "true"

    if not host or not port:
        logging.warning(f"Service {name} missing required annotations.")
        return

    # 1. Generate NGINX config
    nginx_config = generate_nginx_config(host, port, tls)

    # 2. SSH and write config
    write_config_to_remote_nginx(host, nginx_config)

    # 3. TLS cert (optional)
    if tls:
        issue_cert_via_ssh(host)

    # 4. Update Route53
    update_route53_record(host)


def generate_nginx_config(host, port, tls_enabled):
    if tls_enabled:
        return f"""
server {{
    listen 443 ssl;
    server_name {host};

    ssl_certificate /etc/letsencrypt/live/{host}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{host}/privkey.pem;

    location / {{
        proxy_pass http://192.168.0.100:{port};
    }}
}}
"""
    else:
        return f"""
server {{
    listen 80;
    server_name {host};

    location / {{
        proxy_pass http://192.168.0.100:{port};
    }}
}}
"""


def write_config_to_remote_nginx(hostname, config):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname='192.168.1.10',
        username='nginxadmin',
        key_filename='/app/secrets/id_rsa'
    )

    remote_path = f"/etc/nginx/sites-available/{hostname}"
    command = f"echo '{config}' | sudo tee {remote_path} && sudo ln -sf {remote_path} /etc/nginx/sites-enabled/{hostname} && sudo nginx -s reload"

    ssh.exec_command(command)
    ssh.close()


def issue_cert_via_ssh(hostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname='192.168.1.10',
        username='nginxadmin',
        key_filename='/app/secrets/id_rsa'
    )

    command = f"sudo certbot --nginx -d {hostname} --non-interactive --agree-tos -m admin@{hostname}"
    ssh.exec_command(command)
    ssh.close()


def update_route53_record(fqdn):
    hosted_zone_id = os.environ['ROUTE53_ZONE_ID']
    public_ip = os.environ['NGINX_PUBLIC_IP']

    route53 = boto3.client('route53')

    response = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': fqdn,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': public_ip}]
                    }
                }
            ]
        }
    )
    return response
