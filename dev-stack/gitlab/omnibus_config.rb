
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html
# https://qiita.com/KO_YAmajun/items/1a511a3378a67358bb04
# https://qiita.com/KO_YAmajun/items/b4e894f72697348e3beb
# roles ['monitoring_role']
external_url 'http://192.168.11.2/gitlab'
# external_url 'http://192.168.11.2:30080'
# gitlab_rails['initial_root_password'] = 'root'
gitlab_rails['time_zone'] = 'Tokyo'
gitlab_rails['gitlab_shell_ssh_port'] = 30022
postgresql['enable'] = true
# [OPTION] HTTPS settings
# nginx['listen_port'] = 80
# nginx['listen_https'] = false
# nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.crt"
# nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.key"
# nginx['hsts_max_age'] = 0
# nginx['redirect_http_to_https'] = true
# nginx['redirect_http_to_https_port'] = 80

# [OPTION] GitLab Container Registry
# registry_external_url 'http://192.168.11.2:5000'
# gitlab_rails['registry_enabled'] = true
# gitlab_rails['registry_api_url'] = "http://localhost:5001"
# registry['enable'] = true
# registry_nginx['enable'] = false
# registry['registry_http_addr'] = "0.0.0.0:5001"

# [OPTION] Optimize Puma
# https://docs.gitlab.com/ee/administration/operations/puma.html
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html#optimize-puma
# puma['per_worker_max_memory_mb'] = 1024 # 1GB
# puma['worker_processes'] = 0 # Experimental feature

# [OPTION] Optimize Redis
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html#optimize-sidekiq
# sidekiq['max_concurrency'] = 10

# [OPTION] Optimize Gitaly
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html#optimize-gitaly
# gitaly['configuration'] = {
#   concurrency: [
#     {
#       'rpc' => "/gitaly.SmartHTTPService/PostReceivePack",
#       'max_per_repo' => 3,
#     }, {
#       'rpc' => "/gitaly.SSHService/SSHUploadPack",
#       'max_per_repo' => 3,
#     },
#   ],
#   cgroups: {
#     repositories: {
#       count: 2,
#     },
#     mountpoint: '/sys/fs/cgroup',
#     hierarchy_root: 'gitaly',
#     memory_bytes: 500000,
#     cpu_shares: 512,
#   },
# }
gitaly['env'] = {
  'MALLOC_CONF' => 'dirty_decay_ms:1000,muzzy_decay_ms:1000',
  'GITALY_COMMAND_SPAWN_MAX_PARALLEL' => '2'
}

# [OPTION] Disable monitoring by Prometheus/Grafana/Alertmanager
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html#disable-monitoring
prometheus_monitoring['enable'] = true
# prometheus_monitoring['enable'] = false
prometheus['enable'] = true
# prometheus['enable'] = false
prometheus['listen_address'] = '0.0.0.0:9090'
# prometheus['monitor_kubernetes'] = false
# gitlab_exporter['enable'] = true

# Enable service discovery for Prometheus
# consul['enable'] = true
# consul['enable'] = false
# consul['monitoring_service_discovery'] = true
# consul['configuration'] = {
#    retry_join: %w(10.0.0.1 10.0.0.2 10.0.0.3), # The addresses can be IPs or FQDNs
# }
# nginx['enable'] = true
# nginx['enable'] = false
grafana['enable'] = false

# alertmanager['enable'] = false

# [OPTION] Configure how GitLab handles memory
# https://docs.gitlab.com/omnibus/settings/memory_constrained_envs.html#configure-how-gitlab-handles-memory
gitlab_rails['env'] = {
  'MALLOC_CONF' => 'dirty_decay_ms:1000,muzzy_decay_ms:1000'
}

# [OPTION] Disable GitLab agent server (KAS)
# https://docs.gitlab.com/charts/charts/gitlab/kas/index.html
gitlab_rails['gitlab_kas_enabled'] = false
