# Haikubot for Slack

[![Build Status](https://travis-ci.org/hermith/haikubot.svg?branch=master)](https://travis-ci.org/hermith/haikubot)

## Purpose
To increase your team's productivity, I highly recommend having a requirement that every pull-request
is accompanied by a haiku that describes the PR or your mood when developing the PR.

This bot takes all your pull-request haikus that might be spread over several repositories and posts them
to your team's slack! So everyone can enjoy your PR haikus.

PS: Failure to supply an adequate haiku (not 5-7-5 syllables, a lot of filler words, etc.) should result in cake
punishment (getting a cake/snack for the entire team).

## Commands
Haikus are posted directly to the channel configured, but there are also some commands that can be used at any time. All commands are triggered by `@botname` (as configured).

* `show [haiku ID]`, example: `@botname show #3`

   This will post a single haiku by that ID.
* `show from [optional amount] [name]`, example: `@botname show from Danny` or `@botname show from 5 Danny`

   This will post all haikus from that user up to the given amount, the default amount is `3`.
* `show last`

   Posts the newest haiku.
* `stats top [optional amount]`, example: `@botname stats top`

   Posts how many haikus each contributor has posted, default is every user. Limit to e.g. top 3 with `@botname stats top 3`

* `export`, example: `@botname export [optional name]`

   Will post a snippet of all haikus in plaintext, use with `@botname export Danny` to export only haikus by single contributor.

## Prerequisites
### Running locally
#### For running with local storage
* python 3.5
* virtualenv

#### If using a remote postgres DB
* libpq-dev
* python3-dev

### Running with Docker
* Docker, preferably with docker-compose

## Running
1. Activate your virtualenv: `source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Set sequired environment variables: `HAIKUBOT_API_KEY`
    * If using a remote DB also set `HAIKUBOT_DB_PW`
4. Make changes to `config.py`, the most important fields are in the first section.
5. Run the bot with `python bin/run_haikubot.py`

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
* Add a ["field"](https://api.slack.com/docs/message-attachments) or two to the slack message with info like repository.
* Add rating functionality. E.g: "@haikubot rate #69 80 points". Rating is stored and you can pull up best haikus. E.g: "@haikubot top 3 weekly"

## Fork it!
Feel free to play around with it! If you're not using Stash you can easily change it to poll any VCS that has a REST-API,
of course this will require changing the parsing of the JSON a bit.

Feel free to submit pull requests! This bot has been a fun learning experince so the code is a bit messy.
