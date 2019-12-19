FROM elasticsearch:7.2.0

COPY --chown=elasticsearch:elasticsearch elasticsearch.yml /usr/share/elasticsearch/config/

ENV TAKE_FILE_OWNERSHIP 1
ENV ES_JAVA_OPTS "-Xms512m -Xmx512m"

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu