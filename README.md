# MirrorWorldUpdater

---------

**English** | [中文](./README_cn.md)

A plugin to sync any server world to the mirror server

## Dependencies

`mcdreforged >= 2.0.0`

`prime_backup >= 1.7.4`

`minecraft_data_api >= 1.5.0`

## Configure

Configure file: `config/mirror_world_updater/config.json`

> [!IMPORTANT]
> After edit the `config.json` file, you need to use `!!MCDR plugin reload mirror_world_updater` to make this valid.

### `permissions`

Default value:
```
root: int = 0
upstream: int = 1
update: int = 1
abort: int = 1
confirm: int = 1
```

The minimum permission level to use the command

### `upstream_list`

Default value:
```
{
    "server": "survival",
    "server_path": "../survival/server"
},
{
    "server": "mirror",
    "server_path": "../mirror/server"
},
{
    "server": "creative",
    "server_path": "../creative/server"
}
```

The paths of servers you want to sync

### `self_server_path`

Default value: `./server`

The path to the mirror server (destination)

### `world_names`

Default value: `['world']`

World list to sync

For Vanilla servers: `["world"]`

For Spigot servers: `['world', 'world_nether', 'world_the_end']`

### `dimension_region`

Default value:
```
'-1': ['DIM-1/region', 'DIM-1/poi'],
'0': ['region', 'poi'],
'1': ['DIM1/region', 'DIM1/poi']
```
Region files to update

### `count_down`

Default value: `10`

The countdown after executing `!!sync confirm`

### `backup_before_sync`

Default value: `true`

Use [Prime Backup](https://github.com/TISUnion/PrimeBackup) to back up mirror server world before sync

### `ignore_session_lock`

If enabled, `session.lock` file will be ignored when copying the world

### `sync_ignore_files`

Default value: `false`

Example:

For Carpet server, you may not want to sync your carpet settings to mirror server, just put `carpet.conf` into the list like this:
```
"ignore_files": [
    "carpet.conf"
]
```

If enabled, the files or dirs in list will be ignored when copying the world

## Commands

`!!sync`: Display help message

`!!sync upstream`: Set upstream worlds

`!!sync region`: Update the selected regions

`!!sync update`: Sync worlds

`!!sync confirm`: Use after execute back to confirm sync execution

`!!sync abort`: Abort syncing at anytime
