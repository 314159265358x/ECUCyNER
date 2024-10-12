
# internal port

This application should be running under the reverse proxy so that it will safely run.
To achieve this, an internal port should be confirmed.
This example shows how to use internal port to setup.

## configure firewall

Firstly, check the firewall to ensure this port is not allowed for incoming traffic to ensure it is only able to receive the traffic from reverse proxy via loopback.
`ufw status`

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
22/tcp (v6)                ALLOW       Anywhere (v6)
443/tcp (v6)               ALLOW       Anywhere (v6)
```
This shows the service will not be able to access directly. It can only be accessed by reverse proxy.

## configure reverse proxy

Secondly, configure the nginx services, adding the forward rules and point to service.
Edit the site config, which is a server block.
Then add the forward rules.

```
      location /external/url/path {
            proxy_pass http://127.0.0.1:38000; # your internal port here
            proxy_redirect off;
            proxy_http_version 1.1;
            #proxy_set_header Upgrade $http_upgrade;
            #proxy_set_header Connection "upgrade";
            proxy_set_header Host $http_host;

            # Show realip in v2ray access.log
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
```
Finish the editing, and save the file.
Then restart the reverse proxy.
`service nginx restart`

## configure application

Editing the config file `res/settings.json`, change the value of `.listen.port` as the port which has been set in reverse proxy already.

## Reference
How to configure a reverse proxy:
Link: https://guide.v2fly.org/en_US/advanced/wss_and_web.html#nginx-configuration
