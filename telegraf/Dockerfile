FROM telegraf 
RUN apk add --no-cache go git && \
    go build -tags 'inputs' github.com/influxdata/telegraf && \
    mv telegraf /usr/bin/telegraf