# Docker compose
================

## Services

### Grafana
URL: http://localhost:3000/
User: admin
Password: admin

### Kibana
URL: http://localhost:5601/

## Usage 

From a terminal run:
``` docker-compose up --build ```

To exit press CTRL+C and run:
``` docker-compose down ```

To exit and delete stored data, press CTRL+C and run:
``` docker-compose down --volumes --remove-orphans && docker-compose rm -v ```

Firewall configuration to access from other hosts
-------------------------------------------------

```
# Grafana
sudo firewall-cmd --add-port=3000/tcp --permanent
# Kibana
sudo firewall-cmd --add-port=5601/tcp --permanent
sudo firewall-cmd --reload
```
