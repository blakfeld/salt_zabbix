include:
  - salt.minion

zabbix-api-config:
  file.managed:
    - name: /etc/zabbix/api/config.yaml
    - source: salt://zabbix/files/etc/zabbix/api/config.yaml
    - makedirs: true
    - template: jinja
    - context:
      Monitors_DIR: {{ pillar['zabbix-api']['Monitors_DIR'] }}
      Templates_DIR: {{ pillar['zabbix-api']['Templates_DIR'] }}
      Zabbix_User: {{ pillar['zabbix-api']['Zabbix_User'] }}
      Zabbix_Pass: {{ pillar['zabbix-api']['Zabbix_Pass'] }}
      Zabbix_URL: {{ pillar['zabbix-api']['Zabbix_URL'] }}

zabbix-templates:
  file.recurse:
    - name: {{ pillar['zabbix-api']['Templates_DIR'] }}
    - source: salt://zabbix/files/etc/zabbix/api/templates
    - require:
      - file: zabbix-api-config
      - pip: pyzabbix

zabbix-add-monitors-script:
  file.managed:
    - name: /etc/zabbix/api/add_monitors.py
    - source: salt://zabbix/files/etc/zabbix/api/add_monitors.py
    - makedirs: true
    - mode: 755
    - require:
      - file: zabbix-api-config
      - pip: pyzabbix

{% for each_minion, each_mine in salt['mine.get']('*', 'grains.item').iteritems() %}
monitor-{{ each_minion }}:
  file.managed:
    - name: {{ pillar['zabbix-api']['Monitors_DIR'] }}{{ each_minion }}
    - source: salt://zabbix/files/etc/zabbix/api/monitors/minion
    - makedirs: true
    - template: jinja
    - context:
      IP: {{ each_mine.ipv4[1] }}
      Hostname: {{ each_mine.host }}
      {% if each_mine.datacenter == 'dcn1' %}
      Proxy: zabnode2
      {% elif each_mine.datacenter == 'dcn2' %}
      Proxy: zabnode1
      {% else %}
      Proxy: zabnode3
      {% endif %}
      Roles: {{ each_mine.roles }}
      Templates: {{ pillar['zabbix-templates'] }}
    - order: last
    - require:
      - module: mine_update

  cmd.wait:
    - name: python /etc/zabbix/api/add_monitors.py {{ each_minion }}
    - require:
      - file: zabbix-add-monitors-script
      - file: zabbix-api-config
      - pip: pyzabbix
    - watch:
      - file: monitor-{{ each_minion }}
{% endfor %}
