# from oauthenticator.gitlab import LocalGitLabOAuthenticator
# from oauthenticator.gitlab import GitLabOAuthenticator

# c.JupyterHub.authenticator_class = LocalGitLabOAuthenticator
# c.LocalGitLabOAuthenticator.gitlab_host = "http://localhost/gitlab/"
# c.LocalGitLabOAuthenticator.client_id = (
#     "ba17208cf245b581f86c9a00c4311d6094c9144094d41acf25cfcf5b3b767f3d"
# )

# c.LocalGitLabOAuthenticator.client_secret = (
#     "gloas-752a4477483d303b2e4b6347bce47c8a4c59c1ac5e6bb2a41ea6ac1634fdc23c"
# )
# c.LocalGitLabOAuthenticator.oauth_callback_url = (
#     "http://localhost/jupyterhub/hub/oauth_callback"
# )
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
c.PAMAuthenticator.admin_groups = {"sudo"}
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
