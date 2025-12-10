# invoke function
aws lambda invoke \
  --function-name=$(terraform output -raw certificate_function_name) \
  --invocation-type RequestResponse \
  --cli-binary-format raw-in-base64-out \
  --payload '{
    "local_path": "/tmp/",
    "bucket_name": "'$(terraform output -raw bucket_id)'",
    "upstream_prefix": "certificate-upstream-zone/"
    }' \
  response.json && cat response.json && rm response.json
