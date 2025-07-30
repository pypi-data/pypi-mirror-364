# Microservice CLI

Tool for manage the talk-point microservices.

## Install

````sh
$ pip install shopcloud-microservice
````

## App

```sh
$ microservice app health
```

## Security

```sh
$ microservice security merge-security-pull-requests
$ microservice security ci-secrets-rolling
```

## Backup

Backup commands (test) (es wird ein Export pro Instanz ausgeführt)

```sh
$ python -m shopcloud_microservice -d -s backup sql-init shopcloud-secrethub:europe-west3:secrethub # initialise backup storage for a instance
$ python -m shopcloud_microservice -d -s backup sql-list-instances # list all known instances from projects.yaml
$ python -m shopcloud_microservice -d -s backup sql-list-databases shopcloud-secrethub:europe-west3:secrethub # list databases on server
$ python -m shopcloud_microservice -d -s backup sql-dump # dumo all databaeses ob all known server from projects.yaml
$ python -m shopcloud_microservice -d -s backup sql-dumo shopcloud-secrethub:europe-west3:secrethub # dump all databases from instance
$ python -m shopcloud_microservice -d -s backup sql-dump shopcloud-secrethub:europe-west3:secrethub:shopcloud-secrethub-api # download a database from instance
$ python -m shopcloud_microservice -d -s backup sql-dump shopcloud-secrethub:europe-west3:secrethub:shopcloud-secrethub-api # download a database from instance
$ python -m shopcloud_microservice -d -s backup sql-download # download all dumpfiles to db-dumps
$ python -m shopcloud_microservice -d -s backup sql-push-to-drive /tmp # sync content from download-folder to specific path
```

## Develop

Entwickle deine Änderungen im develop branch oder feature branch.
Beim mergen des Pull-Requests in den master wird automatisch ein deploy mittels `wheel` und `twine` durchgeführt.
