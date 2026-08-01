FROM apache/polaris-admin-tool:1.6.0

USER root
COPY infra/polaris/admin/bootstrap-jdbc.sh /usr/local/bin/bootstrap-polaris-jdbc
RUN chmod 0555 /usr/local/bin/bootstrap-polaris-jdbc
USER polaris

ENTRYPOINT ["/usr/local/bin/bootstrap-polaris-jdbc"]
