Quotefault API
==============

A RESTful API for interacting with CSH Quotefault, no webgui required!

### Format

```json
{
  "533": {
    "quote": "I can't wait to get to New York and kill everyone", 
    "quoteTime": "Fri, 27 Oct 2017 22:14:31 GMT", 
    "speaker": "Tanat", 
    "submitter": "matted"
  }
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
  "533": {
    "quote": "I can't wait to get to New York and kill everyone", 
    "quoteTime": "Fri, 27 Oct 2017 22:14:31 GMT", 
    "speaker": "Tanat", 
    "submitter": "matted"
  }
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

## `/generatekey/<reason>` : `GET`

Requires a reason as to the use of the API key. A key has a unique owner/reason pair.

#### Output: 

```
91651at924r55egdfac5
```


## Dev Setup
This project is built in Python 3, and all of its dependencies are accesible via pip.

Reccomended setup (from inside your repository directory)
```
python3 -m virtualenv venv # Sets up virtualenve in the venv directory in your working directory
source venv/bin/activate # Activates the virtual environment
pip install -r requirements.txt # Installs all of the dependencies listed in the requirements to the virtualenv
```

At this point all the dependencies are installed, so copy `config.env.py` to `config.py` and fill in fields.
You probably need to set `SERVER_NAME = 127.0.0.1:5000`, which is where flask will put local applications.

All that's left is running it with `flask run`. Flask should automatically find `app.py`,
though you may want to set debug mode with `export FLASK_ENV=development` before you run it.
