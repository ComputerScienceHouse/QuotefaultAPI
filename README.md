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

## `/all`
**Allowed Parameters: `date`, `submitter`**

Example Request: ``

## `/random`
**Allowed Parameters: `date`, `submitter`**

Example Request: `/random?submitter=dante`

## `/newest`
**Allowed Parameters: `date`, `submitter`**

### Example Request: `/newest?submitter=matted`
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

## `/between/<start>/<limit>`
**Allowed Parameters: None :cry:**