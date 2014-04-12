#!/usr/bin/env python
"""

add_monitors.py - Use the Zabbix API to read a file containing
  attributes of our hosts, and then add them to zabbix with the
  appropriate templates applied.

  Based around pengyao's code:
  https://github.com/pengyao/salt-zabbix/blob/a65cff9a24720f4272b3ae20671e144096a10aa1/salt/zabbix/files/etc/zabbix/api/add_monitors.py

"""

import sys
import os.path
import yaml
from pyzabbix import ZabbixAPI
from requests import Session


def _config(config_file):
    '''
    get config
    '''

    config_fd = open(config_file)
    config = yaml.load(config_fd)
    config_fd.close()

    return config


def _create_hostgroup(api_obj, group_name):
    '''
    create hostgroup
    '''

    # Ensure the host group doesn't already exist
    hostgroup_status = api_obj.hostgroup.get(filter={"name": group_name})
    if hostgroup_status:
        print "Hostgroup ({0}) already exists!!!".format(group_name)
        group_id = hostgroup_status[0]["groupid"]
    else:
        hostgroup_status = api_obj.hostgroup.create({"name": group_name})
        if hostgroup_status:
            print "Hostgroup ({0}) successfully created!!! Hooray!".format(group_name)
            group_id = hostgroup_status["groupids"][0]
        else:
            sys.stderr.write(
                "Hostgroup ({0}) creation failed :( Please contact an administrator\n".format(group_name))
            exit(2)

    return group_id


def _create_host(api_obj, hostname, hostip, group_id):
    '''
    create host
    '''

    # Ensure a host doesn't already exist
    host_status = api_obj.host.get(filter={"host": hostname})
    if host_status:
        print "Host ({0}) already exists!!!".format(hostname)
        hostid = api_obj.host.get(filter={"host": hostname})[0]["hostid"]
    else:
        host_status = api_obj.host.create(
            {"host": hostname, "interfaces": [{"type": 1, "main": 1, "useip": 1, "ip": hostip, "dns": "", "port": "10050"}], "groups": [{"groupid": group_id}]})
        print "Host does not exist!"
        if host_status:
            print "Host ({0}) successfully created!!! Hooray!".format(hostname)
            hostid = host_status["hostids"][0]
        else:
            sys.stderr.write(
                "Hostname ({0}) creation failed :( Please contact an adminstrator\n".format(hostname))
            exit(3)

    return hostid


def _get_proxy_id(api_obj, proxy_name):
    '''
    get proxy id
    '''

    proxy_get = api_obj.proxy.get(output="extend", filter={"host": proxy_name})
    proxy_id = proxy_get[0]['proxyid']

    return proxy_id


def _update_proxy(api_obj, hostname, hostid, proxy_name):
    '''
    update the proxy attribute of a host
    '''

    # Get our proxy id
    proxy_id = _get_proxy_id(api_obj, proxy_name)

    # Update the host
    update_status = api_obj.host.update(
        {"hostid": hostid, "proxy_hostid": proxy_id})

    if update_status:
        print "Successfully updated {0} to report to proxy {1}".format(hostname, proxy_name)
    else:
        print "Unable to update {0} to report to proxy {1} :( Please contact an administrator".format(hostname, proxy_name)

def _update_name(api_obj, hostname, hostid, visible_name):
    '''
    Update the name attribute of a host
    '''

    # Update the host
    update_status = api_obj.host.update(
        {"hostid": hostid, "name": visible_name})

    if update_status:
        print "Successfully updated {0} to have the alias{1}".format(hostname, visible_name)
    else:
        print "Unable to update {0} to have teh alias {1} :( Please contact an administrator".format(hostname, visible_name)

def _get_template_ids(api_obj, templates_list):
    '''
    get template ids
    '''
    template_lookup= api_obj.template.get(
        output="extend", filter={"host": "{0}".format(templates_list)})

    if len(template_lookup):
      return template_lookup[0]['templateid']


def _get_hosts_templates(api_obj, hostid):
    '''
    get templates already linked to a host
    '''

    templates_id = []
    templates_result = api_obj.template.get(filter={"hostid": hostid})

    for each_template in templates_result:
        templates_id.append(each_template['templateid'])

    return templates_id


def _link_templates(api_obj, hostname, hostid, templates_list):
    '''
    link templates
    '''

    all_templates = []
    templates_ids = []

    for template in templates_list:
        # Get the proper ids of our templates
        templates_ids.append(_get_template_ids(api_obj, template))

    # Get what templates we have currently linked
    curr_linked_templates = _get_hosts_templates(api_obj, hostid)

    for each_template in templates_ids:
        if each_template in curr_linked_templates:
            print "Host ({0}) is already linked to {1}".format(hostname, each_template)
        else:
            print "Host ({0}) will be linked to {1}".format(hostname, each_template)
        all_templates.append(each_template)

    # Merge Template lists
    for each_template in curr_linked_templates:
        if each_template not in all_templates:
            all_templates.append(each_template)

    # Prepare for Zabbix
    templates_list = []
    for each_template in all_templates:
        templates_list.append({"templateid": each_template})

    # Update host to link to template
    update_status = api_obj.host.update(
        {"hostid": hostid, "templates": templates_list})
    if update_status:
        print "Host ({0}) successfully linked to templates!!! Hooray!".format(hostname)
    else:
        print "Host ({0}) could not be successfully linked to templates :( Please contact an administrator".format(hostname)


def _main():
    '''
    main function
    '''

    # Get hosts from CLI
    hosts = []
    if len(sys.argv) > 1:
        hosts = sys.argv[1:]

    # Load Config
    config_dir = os.path.dirname(sys.argv[0])
    if config_dir:
        config_file = config_dir + "/config.yaml"
    else:
        config_file = "config.yaml"

    # Get Config Options
    config = _config(config_file)
    Monitor_DIR = config["Monitors_DIR"]
    Zabbix_URL = config["Zabbix_URL"]
    Zabbix_User = config["Zabbix_User"]
    Zabbix_Pass = config["Zabbix_Pass"]

    # Disable SSL verify
    s = Session()
    s.verify = False

    # Login to Zabbix
    zapi = ZabbixAPI(Zabbix_URL, s)
    zapi.login(Zabbix_User, Zabbix_Pass)

    # Iterate through hosts
    for each_host in hosts:
        each_config_fd = open(Monitor_DIR + each_host)
        each_config = yaml.load(each_config_fd)
        each_config_fd.close()

        # Get config attributes
        each_ip = each_config["IP"]
        each_hostname = each_config["Hostname"]
        each_proxy = each_config["Proxy"]
        each_hostgroup = each_config["Hostgroup"]
        each_templates = each_config["Templates"]

        # Create Hostgroup
        group_id = _create_hostgroup(zapi, each_hostgroup)

        # Create Host
        hostid = _create_host(zapi, each_host, each_ip, group_id)

        # If machine needs a proxy, set that attribute.
        if each_proxy:
            _update_proxy(zapi, each_host, hostid, each_proxy)

        if each_hostname:
            _update_name(zapi, each_host, hostid, each_hostname)

        # Link Templates, if we have any Templates
        if each_templates:
            print each_templates
            _link_templates(zapi, each_host, hostid, each_templates)

if __name__ == "__main__":
    _main()
