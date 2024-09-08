from jupyter_client.localinterfaces import public_ips
import netifaces
# import dockerspawner
# import subprocess

# names = subprocess.check_output(["getent","passwd"])
# names = names.decode()
# names = names.split("\n")
# for i in range(0, len(names)):
#     names[i] = names[i].split(":")[0]
#     print(names[i])
# names = set(names)
# c.Authenticator.allowed_users = names
c = get_config()  # noqa


ip = public_ips()[0]

c.LocalAuthenticator.create_system_users=True
c.LocalAuthenticator.add_user_cmd=['/etc/jupyterhub/add_user.sh']
c.PAMAuthenticator.admin_groups = {'sudo'}

# c.JupyterHub.hub_ip = ip
# c.JupyterHub.spawner_class = SystemUserSpawner

# c.DockerSpawner.image = 'jupyter/scipy-notebook:0f73f7488fa0'
# c.DockerSpawner.host_homedir_format_string = "/home/{username}/jupyterhub"

# c.DockerSpawner.remove_containers = True
# c.DockerSpawner.remove = True


# ip = public_ips()[0]

# c.JupyterHub.hub_ip = ip
# c.JupyterHub.hub_port = 8111

# c.JupyterHub.ip= ip
# c.JupyterHub.port = 8888
# c.JupyterHub.bind_url = 'http://127.0.0.1:8000'
# c.JupyterHub.ip = '0.0.0.0'

c.JupyterHub.hub_connect_ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
c.JupyterHub.hub_id = '0.0.0.0'

c.Spawner.default_url = '/lab'
c.Spawner.notebook_dir = '~/notebook'
# c.Authenticator.allow_all = True
c.Authenticator.admin_users = {
    'admin'
}
c.Authenticator.allowed_users = {
    'penguin'
}
