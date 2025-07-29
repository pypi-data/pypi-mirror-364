ARG APPCD_VERSION="main"
ARG APPCD_ANALYZER="main"

FROM ghcr.io/appcd-dev/appcd:${APPCD_VERSION} AS cli

FROM ghcr.io/appcd-dev/appcd-analyzer:${APPCD_ANALYZER}

USER root

RUN apt-get update && \
    apt-get install -y musl-dev

USER appcd

COPY --from=cli --chown=1001:1001 /root/resources/db/migration /app/resources/db/migration

ENV MIGRATION_SOURCE=file:/app/resources/db/migration

COPY --from=cli /bin/appcd /bin/appcd

ENV PATH="/app/bin/:${PATH}"

ENTRYPOINT [ "/bin/appcd"]

WORKDIR /out

CMD ["server", "--config=/config/server.yaml" ]
