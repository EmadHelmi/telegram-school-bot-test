# School bot

This bot is only for an interview. **Nobody can use this bot for any other reasons.**

## How to run

To install and run code:

``` bash
make && make manage runserver
```

### Install prerequisites 

Installing `docker`, `docker-copmpose`, and `GNU makefile` is required before
installing the code.

### Build and run depenedencies

Make command build required docker images and pull all dependencies using
docker-compose.

``` bash
make up-dep
```

After running this, make sure all required dependencies are running correctly
using `make top-dep` command or viewing docker-compose logs.

### Create postgres tables

After run `up-dep` command, you must create db tables:

``` bash
make manage create_tables
```

After running this you should add some grades, courses and question in each tables.

### Run bot

in the `deploy/school_bot.env` file you should replace `BOT_TOKEN` with your bot token or use `@EmadHelmiExamBot` this Telegram bot instead.

for running the code use this command:

```bash
make mange run-bot
```

### Commiting

To help improve the project, make sure you have the pre-commit hooks installed
before making any commits by running the following command:

``` bash
# if `pre-commit` is not installed in your system:
pip install pre-commit
# and then:
pre-commit install
```

Also you may need install `flake8`, `isort` and `pipenv` systemwide to validate
code style before commit anything. 

``` bash
pip install flake8 isort pipenv
```