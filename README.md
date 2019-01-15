Quotefault API
==============
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Travis](https://travis-ci.org/ComputerScienceHouse/QuotefaultAPI.svg?branch=master)](https://travis-ci.org/ComputerScienceHouse/QuotefaultAPI)


A RESTful API for interacting with CSH Quotefault, no webgui required!

### Format

```json
{
    "id": "533",
    "quote": "I can't wait to get to New York and kill everyone",
    "submitter": "matted",
    "speaker": "Tanat",
    "quoteTime": "Fri, 27 Oct 2017 22:14:31 GMT"
}
```

All `date` paramaters use the format `mm-dd-yyyy`.

If no quotes are found, all routes return 'none'.


## `/<api_key>/all` : `GET`

**Allowed Parameters: `date`, `submitter`, `speaker`**

Example Request: ``

## `/<api_key>/random` : `GET`

**Allowed Parameters: `date`, `submitter`, `speaker`**

Example Request: `/random?submitter=dante`

## `/<api_key>/newest` : `GET`

**Allowed Parameters: `date`, `submitter`, `speaker`**

### Example Request: `/<api_key>/newest?submitter=matted`

#### Output: 

Returns the newest result from the submitter = `matted`

```json
{
    "id": "533",
    "quote": "I can't wait to get to New York and kill everyone",
    "submitter": "matted",
    "speaker": "Tanat",
    "quoteTime": "Fri, 27 Oct 2017 22:14:31 GMT"
}
```

## `/<api_key>/between/<start>/<limit>` : `GET`

**Allowed Parameters: `submitter`, `speaker`**
**Required Parameters: `start`, `limit`**

Route produces a list of quotes between the two dates. 

## `/<api_key>/<qid>` : `GET`

Returns the specified quote. Ignores query parameters.

## `/<api_key>/create` : `PUT`

**Required Parameters: JSON Object**

```json
{
    "quote": "This is an example Quote",
    "submitter": "matted",
    "speaker": "Example Speaker"
}
```

## `/<api_key>/markov` : `GET`

Optionally takes speaker and or submitter query string parameters.

Generates a quote using a Markov chain based on all quotes, optionally filted by speaker or submitter.

## `/<api_key>/markov/<count>` : `GET`

Optionally takes speaker and or submitter query string parameters.

Generates a list of  quotes (length = count) using a Markov chain based on all quotes, optionally filted by speaker or submitter.

## `/generatekey/<reason>` : `GET`

Requires a reason as to the use of the API key. A key has a unique owner/reason pair.

#### Output: 

```
91651at924r55egdfac5
```


## Dev Setup
This project is built in Python 3, and all of its dependencies are accesible via pip.

### Installing Python
[This guide](https://docs.python-guide.org/starting/installation/#installation-guides) should cover installing python
then you need to make sure you [have pip installed](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line).

### Recommended setup
From inside your repository directory run
```
python3 -m virtualenv venv # Sets up virtualenve in the venv directory in your working directory
source venv/bin/activate # Activates the virtual environment
pip install -r requirements.txt # Installs all of the dependencies listed in the requirements to the virtualenv
```

At this point all the dependencies are installed, so copy `config.env.py` to `config.py` and fill in fields.
You probably need to set `SERVER_NAME = 127.0.0.1:5000`, which is where flask will put local applications.

All that's left is running it with `flask run`. Flask should automatically find `app.py`,
though you may want to set debug mode with `export FLASK_ENV=development` before you run it.
