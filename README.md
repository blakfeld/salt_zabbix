## Salt Zabbix

This is a collection of Salt states and pillars I use in production to add new
nodes to a Zabbix monitoring server with correct Proxy, Host, Group, and
Template information using the Zabbix API.

### Pillars

This is a general implementation I've found to be super helpful. Essentially I
have a pillar for each datacenter I expect salt to run on, then I have a list
of the machines I have in that datacenter, and useful attributes about them.
The relevant ones to this project is 'roles', which is what I do all my matching
against.

### States

I have included a basic Salt master state, as well as a Salt minion state. The
minion is an important one as it sets the role on that machine. When running
highstate on the salt master, it will run the add_monitors.py script which
sends the JSON request out to the zabbix server, and adds the needed bits.

### Dependencies

  * pyzabbix

  ``` shell
  pip install pyzabbix
  ```
