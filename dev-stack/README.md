# Homelab Dev Stack

## :scroll: Setup

```bash
# Run all containers
cd ./dev-stack
sudo docker compose up -d

# Setup Nextcloud
sudo docker exec -it homelab-nextcloud /bin/bash -c "sh /root/setup.sh"

# Setup GitLab
sudo docker exec -it homelab-gitlab /bin/bash -c "cat /etc/gitlab/initial_root_password"

# Setup GitLab Runner
sudo docker exec -it homelab-gitlab-runner /bin/bash -c "sed -i 's/concurrent.*/concurrent = 8/' /etc/gitlab-runner/config.toml"
sudo docker exec -it homelab-gitlab-runner /bin/bash -c "cat /etc/gitlab-runner/config.toml"

# Setup Cockpit
# sudo cp ./cockpit/cockpit.conf /etc/cockpit/cockpit.conf && sudo systemctl restart cockpit
```
