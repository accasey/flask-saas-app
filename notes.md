# Application Overview

## Application Architecture

Using:
* `gunicorn` over something else like `uwsgi`.
* `Flask`
* `Celery` (background worker)
    * If you cannot respond nearly instantly - use a background worker
    * Sending e-mail is a good example
    * It is great ast scheduling tasks too.
        * 10 flask servers each with their own cron jobs is likely not good
        * 1 celery scheduler can do the job instead.
* `Redis` (backend for Celery)
    * An in-memory data store
    * Not Python, but many packages for it
    * It is a swiss army knife; cache, message broker, pub/sub
    * Celery uses Redis as a message broker
    * It isn't an alternative to a relational database
* `SQLAlchemy`
    * `PostgreSQL`
* `Click` (CLI)
* `Stripe` (Payment Gateway)
* `Docker`



# Getting Familiar with Docker

## Why is it worth Using Docker

* Running multi-service Flask Apps can be harder than you think
* https://nickjanetakis.com/blog/save-yourself-from-years-of-turmoil-by-using-docker-today

## Installing Docker Engine

The Ubuntu page is [here](https://docs.docker.com/engine/install/ubuntu/)

### Convenience Script
There is also a convenience script here: https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script

This example uses the script at get.docker.com to install the latest release of Docker Engine - Community on Linux. To install the latest testing version, use test.docker.com instead. In each of the commands below, replace each occurrence of `get` with `test`.

```bash
$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh
```

### Run the Docker daemon as a non-root user (Rootless mode)
https://docs.docker.com/engine/security/rootless/

The installation script is available at https://get.docker.com/rootless.
```bash
$ curl -fsSL https://get.docker.com/rootless | sh
```
Make sure to run the script as a non-root user. 
* I also needed to install uidmap
```bash
sudo apt-get install uidmap
```

After running the script
```bash
+ DOCKER_HOST=unix:///run/user/1000/docker.sock /home/andrew/bin/docker version
Client: Docker Engine - Community
 Version:           20.10.2
 API version:       1.41
 Go version:        go1.13.15
 Git commit:        2291f61
 Built:             Mon Dec 28 16:11:26 2020
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.2
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.13.15
  Git commit:       8891c58
  Built:            Mon Dec 28 16:15:23 2020
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v1.4.3
  GitCommit:        269548fa27e0089a8b8278fc4fc781d7f65a939b
 runc:
  Version:          1.0.0-rc92
  GitCommit:        ff819c7e9184c13b7c2607fe6c30ae19403a7aff
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
+ systemctl --user enable docker.service
Created symlink /home/andrew/.config/systemd/user/default.target.wants/docker.service → /home/andrew/.config/systemd/user/docker.service.
[INFO] Installed docker.service successfully.
[INFO] To control docker.service, run: `systemctl --user (start|stop|restart) docker.service`
[INFO] To run docker.service on system startup, run: `sudo loginctl enable-linger andrew`

[INFO] Make sure the following environment variables are set (or add them to ~/.bashrc):

export PATH=/home/andrew/bin:$PATH
export DOCKER_HOST=unix:///run/user/1000/docker.sock
```

### Usage

Use `systemctl --user` to manage the lifecycle of the daemon:
```bash
$ systemctl --user start docker
```
To launch the daemon on system startup, enable the systemd service and lingering:
```bash
$ systemctl --user enable docker
$ sudo loginctl enable-linger $(whoami)
```

## Installing Docker Compose

Not entirely sure what this is for (over and above the docker install above).
You can substitute the release for another, e.g. 1.27.4 (which is the stable release now) with a different release.

https://docs.docker.com/compose/install/

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```

```bash
sudo curl -L https://raw.githubusercontent.com/docker/compose/1.27.4/contrib/completion/bash/docker-compose -o /etc/bash_completion.d/docker-compose
```

## Making sure Docker works on your system

Check to make sure it is working.. Both of these commands should work.
```bash
docker --version
docker-compose --version
```

# Creating a Base Flask App

Dependencies:
* Flask
* pip
* requirements.txt (located in the root directory)


## Working with the `src` directory

### Without Docker

Placed the `snakeeyes` and `config` directories underneath `src`. 

But initially this would not work, i.e. `poetry run flask run` would not work.

I made some modifications to the `src.snakeeyes.app.py` file, just to prefix the config.settings with src, i.e.
* `app.config.from_object("src.config.settings")`

And then I can do this to run the app via gunicorn:
```bash
poetry run gunicorn -w 4 "src.snakeeyes.app:create_app()"
```

If I set the `FLASK_APP` environment variable:
```bash
export FLASK_APP=src.snakeeyes.app
```

Then I can do this:
```bash
peotry run flask run
```


But I could not get the `tool.poetry.scripts` to work.
* It would just say:
    ```bash
    [ModuleOrPackageNotFound]
    No file/folder found for package saas-app
    ```

### With Docker

I needed to modify the `docker-compose.yml` and `Dockerfile` files by adding `src`:
* docker-compose.yml: line 10 - `"src.snakeeyes.app:create_app()"`
* Dockerfile: line 18 - `CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "src.snakeeyes.app:create_app()"`

You can use some docker commands to inspect the contents of the `/snakeeyes` directory:

```bash
# check the running instances - you can add -a
docker ps 
# or
docker ps -a
# Take either the container id or the names and use in the next command, i.e. saas-app_webite_1

# This will log you into the console
docker exec -it saas-app_website_1 /bin/bash

# This will show the files
docker exec -it saas-app_website_1 ls /snakeeyes

# This will show you the docker images
docker images

# Youc an remove containers by using something like
docker rm ID1 ID2
```

https://net2.com/how-to-clean-up-unused-docker-containers-images-and-volumes/


## Configuration Settings

In the `create_app()` function in the `app.py` file there are a few lines for configuration settings:

```python
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("src.config.settings")
    app.config.from_pyfile("settings.py", silent=True)
```

* `instance_relative_config`: This parameter in the FLask constructor is (apparently) telling Flask to look for an instance directory at the same level as snakeeyes.
* `app.config.from_object()`: This method is loading a configuration file, note the module/directories.
    * Should be committed to version control.
    * Should **not** have anything private in there.
* `app.config.from_pyfile()`: This method will load the `setttings.py` file from the `instance` directory (apparently).
    * Excluded from version control
    * Contains private information, e.g.
        * API keys
        * mail logins
        * non-development database passwords
    * Values in this file with overwrite the non-instance settings.
    * You can use an example file, so long as it does not contain any *real* information
        * e.g. `settings.py_production_example` has `DEBUG = False`

In the `settings.py` file you can add in environment variables, and then reference them in the code. 

For example:

```python
# in the settings.py file
HELLO = "Hello World?"

# in the app.py file
return app.config["HELLO"]
```

I had some issues with this in Docker (and possibly natively, e.g. poetry run flask run - I did not check).

with `silent=False` being passed to the `app.config.from_pyfile()` method, I could see that it was not handling the directory structure very well.

So instead of using `instance_relative_config=True` in the `Flask` constructor, I used `instance_path="/snakeeyes"` as this is the directory used in Docker, i.e. off `root`.

Then I had to point the pyfile with a relative path as it was resolving to `/snakeeyes/src/snakeeyes/settings.py` instead of `/snakeeyes/src/instance/settings.py`. So go back up a directory and use the instance directory.

```python
app.config.from_pyfile("../instance/settings.py", silent=False) 
```

Thanks to the Flask documentation as well:
https://flask.palletsprojects.com/en/1.1.x/config/


## Removing the docker containers

```bash
docker-compose rm -f
```

Also run this periodically to clean up disk space
```bash
docker rmi -f $(docker images -qf dangling=true)
```