# Homelab Stacks

## :folder: Folder Structure

- dev-stack
  - main features
  - behind reverse proxy
- exp-stack
  - experimental features
- llm-stack
  - ollama based environment

## :memo: HTTPS化

- 以下、ChatGPTのアドバイス。
- いつかやる

固定IPを持つプライベートネットワーク内のUbuntuサーバで、Dockerを使用してNginxとGitLabのコンテナを自己署名証明書を用いてHTTPS化する手順を以下にまとめます。

### 手順1: 自己署名証明書の作成

まず、ホストマシンで自己署名証明書を作成し、それをNginxとGitLabで使用します。

1. **OpenSSLのインストール**
   必要に応じて、UbuntuサーバにOpenSSLをインストールします。

   ```bash
   sudo apt update
   sudo apt install openssl
   ```

2. **自己署名証明書の作成**
   固定IPに基づいた自己署名証明書を作成します。

   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/server.key -out /etc/ssl/certs/server.crt
   ```

   証明書作成中にプロンプトが表示されるので、次のように固定IPアドレスを`Common Name (CN)`に入力します。

   ```
   Country Name (2 letter code) [AU]:JP
   State or Province Name (full name) [Some-State]:Tokyo
   Locality Name (eg, city) []:Chiyoda
   Organization Name (eg, company) [Internet Widgits Pty Ltd]:My Company
   Organizational Unit Name (eg, section) []:IT Department
   Common Name (e.g. server FQDN or YOUR name) []:192.168.1.100  # 固定IPアドレスを入力
   Email Address []:admin@example.com
   ```

3. **証明書と鍵のパーミッション設定**
   セキュリティを確保するために、秘密鍵のファイルのパーミッションを制限します。

   ```bash
   sudo chmod 600 /etc/ssl/private/server.key
   ```

### 手順2: NginxコンテナのHTTPS対応設定

Nginxコンテナに自己署名証明書を使用してHTTPSを設定します。

1. **NginxのDocker設定を編集**
   `docker-compose.yml`ファイルを使用している場合、Nginxの設定を以下のように修正します。

   ```yaml
   version: '3'
   services:
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - /etc/ssl/certs/server.crt:/etc/ssl/certs/server.crt
         - /etc/ssl/private/server.key:/etc/ssl/private/server.key
         - ./nginx.conf:/etc/nginx/nginx.conf
   ```

2. **Nginx設定ファイルを編集**
   `nginx.conf`（`docker-compose.yml`で指定した設定ファイル）を編集し、HTTPS用の設定を追加します。

   ```nginx
   server {
       listen 443 ssl;
       server_name 192.168.1.100;  # 固定IPアドレス

       ssl_certificate /etc/ssl/certs/server.crt;
       ssl_certificate_key /etc/ssl/private/server.key;

       location / {
           proxy_pass http://gitlab:80;  # GitLabコンテナへのプロキシ設定
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

   server {
       listen 80;
       server_name 192.168.1.100;

       # HTTPリクエストをHTTPSにリダイレクト
       return 301 https://$server_name$request_uri;
   }
   ```

   - `listen 443 ssl;`: NginxがHTTPSリクエストを受け付ける設定。
   - `ssl_certificate`と`ssl_certificate_key`: 自己署名証明書のパスを指定。
   - `proxy_pass`: NginxからGitLabコンテナへのプロキシ設定。

3. **Nginxコンテナの再起動**
   設定変更後、Nginxコンテナを再起動して反映させます。

   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 手順3: GitLabのHTTPS設定

GitLabのコンテナでもHTTPSを使用するために、Nginxコンテナで処理されるHTTPS接続をGitLabに正しく伝える設定を行います。

1. **GitLabの環境変数を設定**
   `docker-compose.yml`ファイルでGitLabの設定を以下のように変更し、外部URLをHTTPSに設定します。

   ```yaml
   services:
     gitlab:
       image: gitlab/gitlab-ce:latest
       hostname: 192.168.1.100
       environment:
         GITLAB_OMNIBUS_CONFIG: |
           external_url 'https://192.168.1.100'
           nginx['listen_port'] = 80
           nginx['listen_https'] = false
   ```

   これにより、GitLabはNginxからプロキシされたHTTPリクエストを受け付ける設定になります。

2. **GitLabコンテナの再起動**
   設定変更後、GitLabコンテナを再起動します。

   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 手順4: ファイアウォールの設定

Ubuntuサーバでファイアウォールが有効になっている場合、HTTPS（ポート443）を許可します。

```bash
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

### 手順5: 動作確認

1. ブラウザで`https://<固定IPアドレス>`にアクセスし、Nginx経由でGitLabが正しく動作していることを確認します。
2. 自己署名証明書を使用しているため、ブラウザで証明書に関する警告が表示されるかもしれません。これはクライアント側の設定で無視するか、証明書を信頼させることで解決できます。

---

これで、自己署名証明書を用いてNginxおよびGitLabコンテナをHTTPS化する手順は完了です。
