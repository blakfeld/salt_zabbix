zabbix-repo:
  file.managed:
    - name: /etc/apt/trusted.gpg.d/zabbix-official-repo.gpg
    - source: salt://zabbix/files/etc/apt/trusted.gpg.d/zabbix-official-repo.gpg

  pkgrepo.managed:
    - name: deb http://repo.zabbix.com/zabbix/2.0/debian wheezy main
    - file: /etc/apt/sources.list.d/zabbix.list
    - require_in:
      - pkg: zabbix-agent
    - require:
      - file: zabbix-repo