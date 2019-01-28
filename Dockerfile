FROM golang:alpine as builder
RUN mkdir /build
COPY main.go /build/
WORKDIR /build
RUN apk add --no-cache git \
    && go get github.com/julienschmidt/httprouter \
    && go get github.com/sirupsen/logrus
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-extldflags "-static"' -o main .

FROM alpine:latest
RUN apk add --no-cache curl jq
COPY --from=builder /build/main /app/
COPY branch-entrypoint.sh /
ENTRYPOINT ["/branch-entrypoint.sh"]
