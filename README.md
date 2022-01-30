# Temperature Monitor

Have you ever wished for an efficiently presented history of all of your fevers?

Have you ever wanted to see it respresented as a local CSV, in a Firebase DB, and visualize it as a plot?

Have you ever wanted to summarize this data using an easy-to-use web API?

And most importantly, have you ever had a spare Raspberry Pi and a DHT11 sensor lying around?

If you answered yes to all the previous questions, then this repo will fulfill all of your fever history dreams!

Monitor your body temperature and get a record of all your past and fevers.

Happy fevering! :tada:

(Covid-19 inspired.)

## Usage

Simple usage, easy life. 

Start the temperature monitoring:
```
start.py
```

Start the web API:
```
web_api.py
```

Request types:
- fever
- temperature

Aggregations:
- daily
- hourly

Operators:
- max
- average
- median

Filters:
- start time
- end time

Request examples are kept secret but can be found at http://localhost:5051/help.
