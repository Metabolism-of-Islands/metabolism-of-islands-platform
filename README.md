# Overview

This repository contains the source code of [Metabolism of Islands](https://metabolismofislands.org/). The following technologies are used:

- Django
- Python
- PostgreSQL 
- PostGIS
- Docker

In order to meaningfully contribute to this project (or clone it and use it for your own purposes), you should ideally be comfortable with (or willing to learn about) the aforementioned technologies. You can make a meaningful contribution if you know either about python/Django, or about HTML/CSS/Javascript (allowing you to contribute with back-end or front-end programming, respectively).

The tech work on Metabolism of Islands has so far be done by a small number of people. However, we are very keen to get others involved. Due to the nature of the work, it would be ideal if you have a background both in urban metabolism/industrial ecology, and in web development. If you are not very familiar with our topic matter, but you are a keen programmer and willing to learn and spend time on this project, then we are happy to assist you in that journey.

# Getting started

DISCLAIMER: the system is currently running in a Linux environment only, but it should also work perfectly fine on Windows or other operating systems if you have Docker running on it. The commands shown below, however, are Linux specific, but these are simply copy / create directory commands that should be easy enough in any OS.

To get started with this project, do the following:

- Clone the repository on your local machine
- Install Docker and specifically [Docker Compose](https://docs.docker.com/compose/)
- Create a number of baseline directories (see below)
- Create a configuration file (see below)
- Build your container
- Import our database

Once this is done, you have completed all the required steps to get the system running. Specific details below:

Let's say you have cloned this repository to /home/user/metabolism-of-islands

    $ cd /home/user/metabolism-of-islands
    $ mkdir src/{media,logs,static}
    $ cp src/ie/settings.sample.py src/ie/settings.py
    $ sudo docker-compose build

MACOS-SPECIFIC INSTRUCTIONS (ignore if using another OS)

This will likely work on Linux and MacOS, but if you have an issue on MacOS, please run another dockerfile instead. Follow the steps below.

    $ sudo docker-compose -f docker-compose.macos.yml build

If you encountered an error regarding the MacOS Python 3.8 Docker Image, you will have to pull this image manually:
(NOTE: in Dec 2025 a new python dockerfile was loaded; check the latest regular dockerfile and update your own commands accordingly)

    $ docker pull python:3.8

Now that this is done, you can run the container like so:

    $ cd /home/user/metabolism-of-islands
    $ sudo docker-compose up

If you are a MacOS user, you should run the docker-compose file of MacOS:

    $ sudo docker-compose -f docker-compose.macos.yml up

END OF MACOS-SPECIFIC INSTRUCTIONS

Wait a few moments, and the containers should be up and running. Your main container (moc_web) will display errors because there is no database yet. Please select your preferred database below and import this as follows:

    $ sudo docker container exec -i moc_db psql -U postgres moc < db.sql

Replace "db.sql" for the name of your database file (which should be uncompressed before loading it). After the database is loaded, you will need to reload your container (hit CTRL+C to stop) followed by:

    $ sudo docker-compose up

And the website should be up and running at [http://0.0.0.0:8888](http://0.0.0.0:8888) and adminer to manage the database is available at [http://0.0.0.0:8080](http://0.0.0.0:8080).

NOTE: there may be additional database migrations that are not yet applied to this database. You can run the migrations by running:

    $ ./migrate

From the root directory of the project. This is a shortcut to migrate any unapplied migrations in the docker container (check out the file contents to see what commands it runs).

# Database

A copy of our database is available for development purposes. Please contact us to obtain a recent version of the database.

# Tutorials

We made some instruction videos for contributors:

![Installing locally](https://multimedia.metabolismofcities.org/media/records/screenshot_0do6q2O.thumbnail.png)

[Installing Metabolism of Islands locally](https://multimedia.metabolismofcities.org/videos/578485/)

![File structure](https://multimedia.metabolismofcities.org/media/records/Screenshot_2020-12-17_18-52-39.thumbnail.png)

[Metabolism of Islands file structure](https://multimedia.metabolismofcities.org/videos/581189/)

Also see the [Programming contributor support videos](https://multimedia.metabolismofcities.org/videos/collection/968/) in our multimedia library.

# What to work on?

Please get in touch with us to discuss contributions. 

# OPTamos

Please see [this OPTamos readme](OPTAMOS.md) to learn more about the OPTamos decision tool and how this is integrated in the Metabolism of Islands website.

**Thanks for your contribution!**
