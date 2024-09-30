# from oauthenticator.gitlab import GitLabOAuthenticator
from oauthenticator.gitlab import LocalGitLabOAuthenticator


c.JupyterHub.authenticator_class = LocalGitLabOAuthenticator
c.LocalGitLabOAuthenticator.gitlab_host = "http://192.168.11.2/gitlab/"
c.LocalGitLabOAuthenticator.client_id = (
    "48bd9e11ee2117910cdc3c9aa56270ffbed41d59ddb6b980e651a589b32c316e"
)

c.LocalGitLabOAuthenticator.client_secret = (
    "gloas-a243b83b36ba9e6ce9b2fcdcb8b0e5649d8e67eeb95b6b3ddd66c26c7d6e2131"
)
c.LocalGitLabOAuthenticator.oauth_callback_url = (
    "http://localhost/jupyterhub/hub/oauth_callback"
)
c.Authenticator.allow_all = True

c.JupyterHub.base_url = "/jupyterhub"
# ログイン後に http://...:8000/user/<username>/lab? へ遷移する設定（Jupyterlabが起動）
c.Spawner.default_url = "/lab"
# Jupyterlabで作成されたノートブックファイルなどが格納されるディレクトリ
c.Spawner.notebook_dir = "~/notebook"
# vscodeユーザのユーザ名
c.Authenticator.admin_users = {
    "vscode",
}
c.Authenticator.allowed_users = {
    "vscode",
}
# c.PAMAuthenticator.admin_groups = {"sudo"}
c.LocalAuthenticator.create_system_users = True
c.LocalAuthenticator.add_user_cmd = ["/etc/jupyterhub/add_user.sh"]
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 60
# 30日 非アクティブのJupyterサーバーのシャットダウン期限
c.NotebookApp.shutdown_no_activity_timeout = 30 * 24 * 60 * 60

# 3日 カーネルのシャットダウン期限
c.MappingKernelManager.cull_idle_timeout = 3 * 24 * 60 * 60

# 1時間 シャットダウンするかどうかの確認インターバル
c.MappingKernelManager.cull_internal = 60 * 60
