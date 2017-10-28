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

## `<api_key>/all` : `GET`
**Allowed Parameters: `date`, `submitter`**

Example Request: ``

## `<api_key>/random` : `GET`
**Allowed Parameters: `date`, `submitter`**

Example Request: `/random?submitter=dante`

## `<api_key>/newest` : `GET`
**Allowed Parameters: `date`, `submitter`**

### Example Request: `<api_key>/newest?submitter=matted`
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

## `<api_key>/between/<start>/<limit>` : `GET`
**Allowed Parameters: None :cry:**

## `<api_key>/create` : `PUT`
**Required Parameters: JSON Object**
```json
{
    "quote": "This is an example Quote",
    "submitter": "matted",
    "speaker": "Example Speaker"
}
```
