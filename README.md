# DontBudge

DontBudge is a basic budgeting app to manage your money during a single pay period. You can create accounts, transactions, bills, and budgets. You can apply categories to your transactions. Select any day of the week as your pay day then set a period of time from a week, a fortnight, a month, a quarter, or a year and have your transactions and budgets be sorted appropriately for that period.

## Installation

DontBudge can be deployed in two ways; the first is to use gunicorn to run the app using `gunicorn run:app`, and the second is to use the official Docker image.

### Without Docker

Make sure you have at least Python 3.9.5 installed. Install the dependencies in `requirements.txt`:

```bash
pip3 install -r requirements.txt

mkdir -p /dontbudge/db
mkdir -p /dontbudge/logs
touch /dontbudge/logs/error.log
touch /dontbudge/logs/access.log

gunicorn --workers 4 --bind 0.0.0.0:9876 --log-level=info --log-file=/dontbudge/logs/error.log --access-logfile=/dontbudge/logs/access.log run:app
```

### Using Docker

The official Docker image can be pulled using `docker pull jerogers/dontbudge:latest`. You can run the image using either `docker` or `docker-compose` (preferred).

#### docker

```bash
docker run \
    -d \
    -e FLASK_SECRET_KEY=<your_key> \
    -v db:/dontbudge/db \
    -v logs:/dontbudge/logs \
    -p 9876:9876 \
    --restart unless-stopped \
    --name dontbudge \
    jerogers/dontbudge:latest
```

#### docker-compose

Using `docker-compose` is the preferred deployment. You can use the following `docker-compose.yml` file or make your own:

```yml
---
version: "2.1"
services:
  dontbudge:
    image: jerogers/dontbudge:latest
    container_name: dontbudge
    environment:
      - FLASK_SECRET_KEY=<your_key>
    ports:
      - 9876:9876
    volumes:
      - /opt/dontbudge/db:/dontbudge/db
      - /opt/dontbudge/logs:/dontbudge/logs
    restart: unless-stopped
```

#### Docker Options

##### Ports

DontBudge runs on port 9876 by default.

##### Environment Variables

* FLASK_SECRET_KEY: The secret key used by flask to sign JWT tokens. This should be a long string of random characters.
* DEBUG: If set, Flask's DEBUG mode will be turned on. NOT RECOMMENDED IN PRODUCTION ENVIRONMENTS.