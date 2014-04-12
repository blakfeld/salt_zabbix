salt-minion:
  cmd.run:
    - name: curl -L http://bootstrap.saltstack.org -o install_salt.sh; sh install_salt.sh git 2014.1
    - unless: salt-minion --version | grep 2014.1

  service.running:
    - enable: true
    - watch:
      - cmd: salt-minion
      - file: salt-minion
      - file: /etc/salt/grains

sync_grains:
  module.wait:
    - name: saltutil.sync_grains

mine_update:
  module.run:
    - name: mine.update
    - require:
      - module: sync_grains

/etc/salt/grains:
  file.managed:
    - source: salt://salt/files/etc/salt/grains
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - context:
        role_list: {{ pillar[ grains['datacenter'] + '_nodes'][grains['host']]['role'] }}
        varnish_status: {{ pillar[grains['datacenter'] + '_nodes'][grains['host']]['varnish'] }}
    - watch_in:
      - module: sync_grains
