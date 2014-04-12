include:
  - salt.minion

salt-master:
  pkg:
    - installed

  file.managed:
    - name: /etc/salt/master
    - source: salt://salt/files/etc/salt/master
    - require:
      - pkg: salt-master

  service.running:
    - enable: true
    - watch:
      - pkg: salt-master
      - file: /etc/salt/master
