import json, json5
# json5 instead of json because of a trailing comma, it is slower but the speed should suffice?
from helpers import *
from db import get_conn, create_table


def main():
    config = load_config()
    config_simple = config["openconfig-interfaces:interfaces"]['interface']
    res = []

    for d in config_simple:
        name = d['name']
        if 'loopback' in name.lower() or 'BDI' in name:
            continue
        description = get_from_dict(d, ['config', 'description'])
        mtu = get_from_dict(d, ['config', 'mtu'], default=None)
        interface = {
            'name': name,
            'description': description,
            'config': d['config'],
            'max_frame_size': mtu,
            'port_channel': get_port_channel(config, name)
        }

        res.append(interface)

    conn = get_conn(user='viliam', initial_db_name='viliam')  # database vpopovec_homework will be created for the user
    cur = conn.cursor()
    create_table(cur)

    insert_rows([r for r in res if 'Port-channel' in r['name']], cur)
    channel_ids = get_channel_ids_from_db(cur)
    assign_port_channel_ids(res, channel_ids)
    insert_rows([r for r in res if 'Port-channel' not in r['name']], cur)

    conn.close()
    cur.close()


def load_config():
    with open('configClear_v2.json', encoding='utf8') as rf:
        jsn = json5.load(rf)
    return jsn['frinx-uniconfig-topology:configuration']


def insert_rows(res, cur):
    for r in res:
        cur.execute(f"""INSERT INTO interfaces (name, description, max_frame_size, config, port_channel_id) 
                            VALUES (%s, %s, %s, %s, %s);""", [r['name'], r['description'], r['max_frame_size'],
                                                              json.dumps(r['config']), r['port_channel']])


def get_channel_ids_from_db(cur):
    cur.execute("SELECT name, id FROM interfaces WHERE name LIKE 'Port-channel%';")
    ids = cur.fetchall()
    return {name: id_ for name, id_ in ids}


def get_port_channel(config, name):
    if 'ethernet' not in name.lower():
        return
    gigabit_name = ''.join([ch for ch in name if ch.isalpha()])  # avoiding regex - faster runtime
    ethernet_name = name.replace(gigabit_name, '')
    config = config['Cisco-IOS-XE-native:native']['interface'][gigabit_name]
    for d in config:
        if d['name'] == ethernet_name and 'Cisco-IOS-XE-ethernet:channel-group' in d:
            return d['Cisco-IOS-XE-ethernet:channel-group']['number']


def assign_port_channel_ids(res, channel_ids):
    for r in res:
        k = f"Port-channel{r['port_channel']}"
        if r['port_channel'] and k in channel_ids:
            r["port_channel"] = channel_ids[k]


if __name__ == '__main__':
    main()
