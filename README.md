# HltvDemoAutoParser
Auto download newest csgo demo from hltv and parse it

`unrar` command needed

## Database

### sql version 
`mysql(mariadb)`

### create
```mysql
CREATE TABLE demo_history (
    matchId varchar(256),
    status varchar(16),
    record_time varchar(32)
);
```

```
status = (
    'Downloading',
    'Parsing',
    'Done',
    'Error'
)
```