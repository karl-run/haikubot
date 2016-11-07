# Haikubot for Slack

[![Build Status](https://travis-ci.org/hermith/haikubot.svg?branch=master)](https://travis-ci.org/hermith/haikubot)

## Purpose
To increase your team's productivity, I highly recommend having a requirement that every pull-request
is accompanied by a haiku that describes the PR or your mood when developing the PR.

This bot takes all your pull-request haikus that might be spread over several repositories and posts them
to your team's slack! So everyone can enjoy your PR haikus.

PS: Failure to supply an adequate haiku (not 5-7-5 syllables, a lot of filler words, etc.) should result in cake
punishment (getting a cake/snack for the entire team).

## Prerequisites
### Running locally
#### For running with local storage
* python 3.5
* virtualenv

#### If using a remote postgres DB
* libpq-dev
* python3-dev

### Running with Docker
* Docker

## Running
1. Activate your virtualenv: `source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Set sequired environment variables: `HAIKUBOT_API_KEY`
    * If using a remote DB also set `HAIKUBOT_DB_PW`
4. Make changes to `config.py`, the most important fields are in the first section.
5. Run the bot with `python run.py`

## Running with Docker (and docker-compose)
1. Set sequired environment variables: `HAIKUBOT_API_KEY`
    * If using a remote DB also set `HAIKUBOT_DB_PW`
2. `docker-compose build`
3. `docker-compose up -d`

## Running tests
1. Make sure you did step 1 and 2 in under the "Running" section.
2. Run with coverage: `py.test --cov=./bot --cov-report term-missing`

## TODO
* Add commands for making adding and deleting haikus through the bot
* Use ORM objects instead of working with dicts (and clean up how haikus are passed around)
* Clean up how commands are handled, it's just a big 'ole messy method at the moment.
* Add a ["field"](https://api.slack.com/docs/message-attachments) or two to the slack message with info like repository.
* Make "show from" command list the newest haikus, not the oldest.
* Add rating functionality. E.g: "@haikubot rate #69 80 points". Rating is stored and you can pull up best haikus. E.g: "@haikubot top 3 weekly"

## Fork it!
Feel free to play around with it! If you're not using Stash you can easily change it to poll any VCS that has a REST-API,
of course this will require changing the parsing of the JSON a bit.

Feel free to submit pull requests! This bot has been a fun learning experince so the code is a bit messy.
