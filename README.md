# Conductor Challenge - SearchCounter

<p align="center">
<a href="https://travis-ci.com/stenioaraujo/conductor-searchcounter"><img src="https://travis-ci.com/stenioaraujo/conductor-searchcounter.svg?token=fKuRPxKq9xKZBfScGjW2&branch=master" alt="Build Status" /></a>
<a href="https://github.com/stenioaraujo/conductor-searchcounter"><img src="https://img.shields.io/badge/Python-3.7-informational.svg?logo=python&style=popout-square" alt="Tested on Python 3.7" /></a>
</p>

<p align="center">
<b>conductor_searchcounter</b> is a module that contains the class SearchCounter, a sliding window counter that tracks how many searches have occured in a given time period. It also has a <b>CLI</b> :)
</p>

## Overview

### Assumptions

- Any new search added to the search history has a timestamp that is equal or greater than the last search added
- The list of Terms are passed to the `SearchCounter` object at instantiation time
- The terms can be reused for any search any amount of times
- There will always be a term to choose from
- the id is `uuid.uuid4()`
- the timestamp is nanoseconds since the epoch

### Architectural decisions:

- `SearchCounter` is the class responsible for manipulating the sliding window
- `SearchCounter` communicates with a `DAO`, which saves the data. The library has two DAOs:
  - `DAOList`: saves the data in a list in memory, there is no persistence on it. **If no DAO is specified, this one is used by default.**
  - `DAOSqlite`: saves the data in a SQLite database, it is used for persistence purposes. One may choose to use it in `:memory:` however.
- The CLI is not interactive, therefore we need persistence for the search history
- SQLite is used as database for persistence
- to retrieve the searches, binary search is used, and because there is an assumption that all searches are added one after the other with incrementing timestamps, the list behind (or table) has its elements sorted. Which gives us `O(log(n))` where `n` is the number of searches
  - In the case of the SQLite database, there is an indece for timestamp, which makes the inserts also `O(log(n))` in comparasion with `O(1)` on the list case
- The classes **ARE NOT** thread safe.

## Requirements

This library was tested on Ubuntu 18.04, the following was used:

- [python 3.7](https://www.python.org/downloads/release/python-370/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [pipenv](https://docs.pipenv.org/en/latest/install/#installing-pipenv)

One can install the requirements with the following script:

``` bash
sudo apt-get update
sudo apt-get install -y python3.7 python3-pip
pip3 install pipenv
```

## Testing

``` bash
git clone https://github.com/stenioaraujo/conductor-searchcounter
cd conductor-searchcounter
pipenv install --dev
pipenv run tox
```

## Install locally

``` bash
git clone https://github.com/stenioaraujo/conductor-searchcounter
cd conductor-searchcounter
pipenv run pip install .
pipenv shell
conductor-searchcounter
python # to start the interpreter
```

Any python application inside this virtual evnrionoment will have access to the `conductor_searchcounter` library. Also the `conductor-searchcounter` CLI will be available inside the virtual environment.

## Install Globally

``` bash
git clone https://github.com/stenioaraujo/conductor-searchcounter
python3.7 -m pip install conductor-searchcounter/
conductor-searchcounter
python3.7 # to start the interpreter
```

Other python applications on the system will have access to the `conductor_searchcounter` library. Also the `conductor-searchcounter` CLI will be available on the system.

## Usage

### Library

The `SearchCounter` class can be access through the `conductor_searchcounter` library, bellow it is shown how to use the features available.

Those commands can be ran directly on the python interpreter started on the preivous sections.

- Using `DAOList`:

``` python
import time

from conductor_searchcounter.counter import SearchCounter


terms = ["job", "conductor", "how to get hired at conductor"]
sc = SearchCounter(terms)

# Add two searches to the search history, the search term is assigned randomly
# from the attached list of search terms. A random uuid is added to each
# search as well.
sc.increment()
sc.increment()

# Wait one second and see how many searches happened in the past second
#   No search happened in the past second, because we waited one second in
#   order to run this query
time.sleep(1)

print(sc.num_arbitrary_lookback(1))  # Should print 0

# Add another one and wait two seconds
sc.increment()
time.sleep(2)

# Add two more
sc.increment()
sc.increment()

# Since we waited two seconds, we only have two in the past two seconds
print(sc.num_arbitrary_lookback(1))  # Should print 2
print(sc.num_arbitrary_lookback(2))  # Should print 2

# Before waiting two seconds, we added another search
print(sc.num_arbitrary_lookback(3))  # Should print 3

# The only way to reach the first searches we added is by going over three
# seconds (the total we waiter)
print(sc.num_arbitrary_lookback(4))  # Should print 5

# Print the most common term in the last four seconds
print(sc.most_common_term(4))
```

- Using `DAOSqlite`:

``` python
import sqlite3
import time

from conductor_searchcounter.counter import SearchCounter
from conductor_searchcounter.dao import DAOSqlite


# Connect to a SQLite database. It is fine if the file doesn't exist at
# first
#   The tables will be initialized when the DAOSqlite is istantiated
#   If the database already exist, the data in it will be reutilized
database = "search_history.db"
conn = sqlite3.connect(database)

dao = DAOSqlite(conn)
terms = ["job", "conductor", "how to get hired at conductor"]
sc = SearchCounter(terms, dao)

# Add two searches to the search history, the search term is assigned randomly
# from the attached list of search terms. A random uuid is added to each
# search as well.
sc.increment()
sc.increment()

# Wait one second and see how many searches happened in the past second
#   No search happened in the past second, because we waited one second in
#   order to run this query
time.sleep(1)

print(sc.num_arbitrary_lookback(1))  # Should print 0

# Add another one and wait two seconds
sc.increment()
time.sleep(2)

# Add two more
sc.increment()
sc.increment()

# Since we waited two seconds, we only have two in the past two seconds
print(sc.num_arbitrary_lookback(1))  # Should print 2
print(sc.num_arbitrary_lookback(2))  # Should print 2

# Before waiting two seconds, we added another search
print(sc.num_arbitrary_lookback(3))  # Should print 3

# The only way to reach the first searches we added is by going over three
# seconds (the total we waiter)
print(sc.num_arbitrary_lookback(4))  # Should print 5

# Print the most common term in the last four seconds
print(sc.most_common_term(4))

# End the database connection
conn.close()
```

### CLI

The CLI implementation makes use of `DAOSqlite` in order to allow persistence. When using the CLI one needs to pass the path to the SQLite database and the terms that will be used on the searches. There are two ways of doing this, inline or Environment Variables:

- Pass database and terms **Inline**

``` bash
DATABASE=/tmp/search_history.db
TERM1=job
TERM2=conductor
TERM3="how to get hired at conductor"

conductor-searchcounter --database $DATABASE increment --term "$TERM1" --term "$TERM2" --term "$TERM3"
conductor-searchcounter --database $DATABASE increment --term "$TERM1" --term "$TERM2" --term "$TERM3"
sleep 1

conductor-searchcounter --database $DATABASE num-arbitrary-lookback 1

conductor-searchcounter --database $DATABASE increment --term "$TERM1" --term "$TERM2" --term "$TERM3"
sleep 2

conductor-searchcounter --database $DATABASE increment --term "$TERM1" --term "$TERM2" --term "$TERM3"
conductor-searchcounter --database $DATABASE increment --term "$TERM1" --term "$TERM2" --term "$TERM3"

conductor-searchcounter --database $DATABASE num-arbitrary-lookback 1
conductor-searchcounter --database $DATABASE num-arbitrary-lookback 2
conductor-searchcounter --database $DATABASE num-arbitrary-lookback 3
conductor-searchcounter --database $DATABASE num-last-minute
conductor-searchcounter --database $DATABASE most-common-term 10
```

- Pass database and terms as **Environment Variables**

``` bash
export CONDUCTOR_SEARCHCOUNTER_DATABASE=/tmp/search_history.db
export CONDUCTOR_SEARCHCOUNTER_INCREMENT_TERMS="job hired conductor" # terms are split by white space

conductor-searchcounter increment
conductor-searchcounter increment
sleep 1

conductor-searchcounter num-arbitrary-lookback 1

conductor-searchcounter increment
sleep 2

conductor-searchcounter increment
conductor-searchcounter increment

conductor-searchcounter num-arbitrary-lookback 1
conductor-searchcounter num-arbitrary-lookback 2
conductor-searchcounter num-arbitrary-lookback 3
conductor-searchcounter num-last-minute
conductor-searchcounter most-common-term 10
```

### Docker

> **Note**: There is a compiled image at Docker Hub, if you just want to skip the build process. [stenioaraujo/conductor-searchcounter](https://hub.docker.com/r/stenioaraujo/conductor-searchcounter)

- Build the image

``` bash
docker build -t stenioaraujo/conductor-searchcounter .
```

- Using the image

The image works similar to the CLI, the only difference is how you access the SQLite database. To access the database using the container, you need to mount the container directory `/data` to your local machine, otherwise, the data won't persist.

If you wish to use the same Environment Variables as the CLI, they are still available on the container:
- `CONDUCTOR_SEARCHCOUNTER_DATABASE`; and
- `CONDUCTOR_SEARCHCOUNTER_INCREMENT_TERMS`

Using the container is very simple

``` bash
docker run --rm -it -v $PWD/conductor_searchcounter_data:/data stenioaraujo/conductor-searchcounter increment --term job --term conductor

docker run --rm -it -v $PWD/conductor_searchcounter_data:/data -e "CONDUCTOR_SEARCHCOUNTER_INCREMENT_TERMS=job conductor" stenioaraujo/conductor-searchcounter increment

docker run --rm -it -v $PWD/conductor_searchcounter_data:/data stenioaraujo/conductor-searchcounter num-last-minute
```
