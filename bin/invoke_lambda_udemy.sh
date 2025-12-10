# invoke function
aws lambda invoke \
  --function-name=$(terraform output -raw udemy_function_name) \
  --invocation-type RequestResponse \
  --cli-binary-format raw-in-base64-out \
  --payload '{
    "url": "'$1'",
    "bucket_name": "'$(terraform output -raw bucket_id)'",
    "upstream_prefix": "udemy-upstream-zone/"
    }' \
  response.json && cat response.json && rm response.json
