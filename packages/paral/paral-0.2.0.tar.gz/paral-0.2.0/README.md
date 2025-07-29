# Parallel (paral)
An Git User/Credential Switcher

## Install
```shell
pipx install paral
```

uv: 
```shell
uv tool install paral
```

## how to use
### Temporarily switch users
```shell
$ paral env
```
### Add User
```shell
$ paral user add
```
### Delete User
```shell
$ paral user delete
```
### Switch User
```shell
$ paral user switch

# or
$ paral switch
```
#### Apply account switching to local only
```shell
$ paral user switch --local
```
### Add Alias
```shell
$ paral alias add
```
### Delete Alias
```shell
$ paral alias delete
```

## Feature
- Terminal-Based UI
- Manage multiple Git users
- Manage Git credential informations and switch between credentials to use
- Aliases

## Requirements
- Python
- Git
- GCM Core

## Todo
- Golang Port
    - Need to write a parser for gitconfig