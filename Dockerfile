FROM alpine:latest

ADD michawan-webhook /michawan-webhook
ENTRYPOINT ["./michawan-webhook"]