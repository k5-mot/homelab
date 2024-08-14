#!/usr/bin/env bash

cd /var/www/html

while [ ! -e ./config/config.php ]; do
    sleep 10
done
sed -i -e "21a 'overwritehost' => 'localhost'," ./config/config.php
sed -i -e "22a 'overwritewebroot' => '/nextcloud'," ./config/config.php
