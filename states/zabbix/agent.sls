include:
  - zabbix.repo

zabbix-agent:
  pkg.installed:
    - require:
      - file: zabbix-repo
      - pkgrepo: zabbix-repo

  file.managed:
    - name: /etc/zabbix/zabbix_agentd.conf
    - source: salt://zabbix/files/etc/zabbix/zabbix_agentd.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - context:
      server: {{ pillar['zabbix-agent']['zabbix_server'] }}

  service:
    - running
    - sig: zabbix_agentd
    - enable: true
    - require:
      - pkg: zabbix-agent
    - watch:
      - pkg: zabbix-agent
      - file: zabbix-agent
      - file: /etc/zabbix/zabbix_agentd.d/*

zabbix-sender:
  pkg.installed:
    - require:
      - pkgrepo: zabbix-repo
