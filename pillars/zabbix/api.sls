zabbix-api:
  Zabbix_URL: https://monitoring.tld/zabbix/
  Zabbix_User: salt
  Zabbix_Pass: password
  Monitors_DIR: /etc/zabbix/api/monitors/
  Templates_DIR: /etc/zabbix/api/templates/

zabbix-templates:
  global:
    - Template Template OS Linux
    - Template Disk Performance

  webserver:
    - Template Apache Stats
    - Template Web Node

  fileserver:
    - Template SNMP_Dell

  cacheserver:
    - Template Varnish
    - Template Varnish Backends
