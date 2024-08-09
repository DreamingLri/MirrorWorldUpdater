# MirrorWorldUpdater

---------

**中文** | [English](./README.md)

一个用来同步任何服务器世界到目标服务器的插件

## 依赖需求

`mcdreforged >= 2.0.0`

`prime_backup >=1.7.4`

## 配置

配置文件: `config/mirror_world_updater/config.json`

> [!IMPORTANT]
> 修改 `config.json` 之后, 你需要使用 `!!MCDR plugin reload mirror_world_updater` 来确保配置文件生效

### `permission_level`

默认值:
```
root: int = 0
upstream: int = 1
update: int = 1
abort: int = 1
confirm: int = 1
```

使用命令的最低权限等级

### `upstream_list`

默认值:
```
"upstream_list": [
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
    ]
```

用于设置同步的服务器及其地址

### `self_server_path`

默认值: `./server`

镜像服务器的路径（你要同步到的服务器地址）

### `world_names`

默认值: `['world']`

需要同步的世界列表

~~香草~~原版服务端: `["world"]`

Spigot 服务端: `['world', 'world_nether', 'world_the_end']`

### `count_down`

默认值: `10`

执行 `!!sync confirm` 后的倒数时间

### `backup_before_sync`

默认值: `true`

使用 [Prime Backup](https://github.com/TISUnion/PrimeBackup) 插件在你同步世界前进行备份，~~防小天才误操作~~

### `ignore_session_lock`

默认值: `true`

如果启用，拷贝世界时将忽略 `session.lock` 文件

### `sync_ignore_files`

默认值: `false`

举例:

对于Carpet服务器，你也许并不想同步你的carpet设置，只需要将`carpet.conf`这个文件添加到列表中，就能避免同步:
```
"ignore_files": [
    "carpet.conf"
]
```


如果启用，拷贝世界时将忽略位于`ignore_files`这些文件夹和文件

## 命令

`!!sync`: 展示帮助页面

`!!sync upstream`: 设置上传服务器列表

`!!sync update`: 同步世界

`!!sync confirm`: 再次确认是否进行同步

`!!sync abort`: 在任何时候键入此指令可中断同步
