FROM quay.io/minio/minio
ENV MINIO_ROOT_USER=${MINIO_ROOT_USER} \
    MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
CMD ["server", "/data", "--console-address", ":9001"]
EXPOSE 9000 9001
