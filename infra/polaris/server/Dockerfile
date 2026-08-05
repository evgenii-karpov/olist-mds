FROM apache/polaris:1.6.0

USER root
COPY infra/polaris/server/application.properties /opt/olist/polaris/application.properties
COPY infra/polaris/server/start.sh /usr/local/bin/start-olist-polaris
RUN chmod 0444 /opt/olist/polaris/application.properties \
    && chmod 0555 /usr/local/bin/start-olist-polaris
USER polaris

ENTRYPOINT ["/usr/local/bin/start-olist-polaris"]
