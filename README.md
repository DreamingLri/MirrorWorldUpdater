# MirrorWorldUpdater

---------

**English** | [中文](./README_cn.md)

A plugin to sync any server world to the mirror server

## Configure

Configure file: `config/mirror_world_updater/config.json`

### `permission_level`

Default value: `2`

The minimum permission level to use the command

### `upstream_list`

Default value:
```json
"upstream_list": [
        {
            "server": "survival",
            "server_path": "../survival1.21/server"
        },
        {
            "server": "mirror",
            "server_path": "../mirror/server"
        },
        {
            "server": "creative",
            "server_path": "../creative/server"
        }
    ]
```

### `self_server_path`

Default value: `./server`

The path to the mirror server (destination)

### `world_names`

Default value: `['world']`

World list to sync

For Vanilla servers: `["world"]`

For Spigot servers: `['world', 'world_nether', 'world_the_end']`

### `count_down`

Default value: `10`

The countdown after executing `!!sync confirm`

### `backup_before_sync`

Default value: `true`

Use [Prime Backup](https://github.com/TISUnion/PrimeBackup) to back up mirror server world before sync



### `ignore_session_lock`

If enabled, `session.lock` file will be ignored when copying the world

## Commands

`!!sync`: Display help message

`!!sync upstream`: Set upstream worlds

`!!sync update`: Sync worlds

`!!sync confirm`: Use after execute back to confirm sync execution

`!!sync abort`: Abort syncing at anytime
