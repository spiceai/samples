FROM apache/superset
# Switching to root to install the required packages
USER root
# https://github.com/influxdata/flightsql-dbapi
RUN pip install flightsql-dbapi
# Switching back to using the `superset` user
USER superset