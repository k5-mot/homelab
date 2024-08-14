# Homelab Dev Stack

## :scroll: Setup

```bash
cd ./dev-stack
sudo docker compose up -d
sudo docker exec -it homelab-nextcloud /bin/bash -c "sh /root/setup.sh"
sudo docker exec -it homelab-gitlab /bin/bash -c "cat /etc/gitlab/initial_root_password"
# sudo cp ./cockpit/cockpit.conf /etc/cockpit/cockpit.conf && sudo systemctl restart cockpit
```
