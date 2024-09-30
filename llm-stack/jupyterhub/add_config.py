# from oauthenticator.gitlab import GitLabOAuthenticator
from oauthenticator.gitlab import LocalGitLabOAuthenticator
import os

### PAM Authenticator
# c.PAMAuthenticator.admin_groups = {"sudo"}
# c.Authenticator.admin_users = {
#     "vscode",
# }
# c.Authenticator.allowed_users = {
#     "vscode",
# }

### GitLab OAuth
c.JupyterHub.authenticator_class = LocalGitLabOAuthenticator
c.LocalGitLabOAuthenticator.oauth_callback_url = str(os.getenv("OAUTH_CALLBACK_URL"))
c.LocalGitLabOAuthenticator.client_id = str(os.getenv("GITLAB_CLIENT_ID"))
c.LocalGitLabOAuthenticator.client_secret = str(os.getenv("GITLAB_CLIENT_SECRET"))
c.Authenticator.allow_all = True

### Domain settings
c.JupyterHub.base_url = "/jupyterhub"
c.Spawner.default_url = "/lab"

### User settings
c.Spawner.notebook_dir = "~/notebook"
c.LocalAuthenticator.create_system_users = True
c.LocalAuthenticator.add_user_cmd = ["/etc/jupyterhub/add_user.sh"]

### Timeout
# Timeout after start notebook
c.Spawner.start_timeout = 120
# Timeout after connection
c.Spawner.http_timeout = 60

### Auto shutdown
# Auto shutdown inactive notebook after 30 days
c.NotebookApp.shutdown_no_activity_timeout = 30 * 24 * 60 * 60
# Auto shutdown inactive kernel after 3 days
c.MappingKernelManager.cull_idle_timeout = 3 * 24 * 60 * 60
# Check if shutdown once 1 hour
c.MappingKernelManager.cull_internal = 60 * 60
