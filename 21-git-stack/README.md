# GIT Stack

## Initialization

### GitLab

```bash
# Get root password
sudo docker exec -it homelab-gitlab /bin/bash -c "cat /etc/gitlab/initial_root_password"
```

### GitLab Runner

```bash
# Change concurrent processes
sudo docker exec -it homelab-gitlab-runner /bin/bash -c "sed -i 's/concurrent.*/concurrent = 8/' /etc/gitlab-runner/config.toml"
sudo docker exec -it homelab-gitlab-runner /bin/bash -c "cat /etc/gitlab-runner/config.toml"
```
