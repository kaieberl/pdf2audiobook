#! /bin/bash

curl localhost:8080 -v \
  -X POST \
  -H "Content-Type: text/plain" \
  -H "ce-id: 123451234512345" \
  -H "ce-specversion: 1.0" \
  -H "ce-time: 2022-12-31T00:00:00.0Z" \
  -H "ce-type: google.cloud.storage.object.v1.finalized" \
  -H "ce-source: //storage.googleapis.com/projects/<project_id>/buckets/<bucket_name>" \
  -H "ce-subject: objects/<last_file>.csv" \
  -d '{
        "bucket": "<bucket_name>",
        "contentType": "text/plain",
        "kind": "storage#object",
        "md5Hash": "...",
        "metageneration": "1",
        "name": "<last_file>.csv",
        "size": "352",
        "storageClass": "MULTI_REGIONAL",
        "timeCreated": "2022-12-31T00:00:00.0Z",
        "timeStorageClassUpdated": "2022-12-31T00:00:00.0Z",
        "updated": "2022-12-31T00:00:00.0Z"
      }'