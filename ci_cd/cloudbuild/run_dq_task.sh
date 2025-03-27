#!/bin/bash
set -e

YAML_CONFIG_GCS_PATH="$USER_CLOUDDQ_YAML_CONFIGS_GCS_PATH/$ENVIRONMENT/$MODEL_NAME-$ENVIRONMENT.yaml"
echo "Model filepath provided: $YAML_CONFIG_GCS_PATH"

FULL_TASK_NAME="${TASK_NAME}-${MODEL_NAME}-${ENVIRONMENT}-2"
echo "Creating Dataplex DQ task: ${FULL_TASK_NAME}"

gcloud dataplex tasks create \
    --location="${DATAPLEX_REGION_ID}" \
    --lake="${DATAPLEX_LAKE_ID}" \
    --trigger-type=ON_DEMAND \
    --execution-service-account="$DATAPLEX_TASK_SERVICE_ACCOUNT" \
    --spark-python-script-file="gs://${DATAPLEX_PUBLIC_GCS_BUCKET_NAME}/clouddq_pyspark_driver.py" \
    --spark-file-uris="gs://${DATAPLEX_PUBLIC_GCS_BUCKET_NAME}/clouddq-executable.zip","gs://${DATAPLEX_PUBLIC_GCS_BUCKET_NAME}/clouddq-executable.zip.hashsum","${YAML_CONFIG_GCS_PATH}" \
    --execution-args=^::^TASK_ARGS="clouddq-executable.zip, ALL, ${YAML_CONFIG_GCS_PATH}, --gcp_project_id='${GOOGLE_CLOUD_PROJECT}', --gcp_region_id='${DATAPLEX_REGION_ID}', --gcp_bq_dataset_id='${TARGET_BQ_DATASET}', --target_bigquery_summary_table='${GOOGLE_CLOUD_PROJECT}.${TARGET_BQ_DATASET}.${TARGET_BQ_TABLE}'," \
    "$FULL_TASK_NAME"

echo "Task created. Waiting for task ${FULL_TASK_NAME} to complete..."

# Poll for task status until it is either SUCCEEDED or FAILED
while true; do
  TASK_STATUS=$(gcloud dataplex tasks describe "${FULL_TASK_NAME}" \
    --lake="${DATAPLEX_LAKE_ID}" \
    --location="${DATAPLEX_REGION_ID}" \
    --format="value(state)")
  echo "Current task status: ${TASK_STATUS}"

  if [[ "${TASK_STATUS}" == "ACTIVE" || "${TASK_STATUS}" == "SUCCEEDED" || "${TASK_STATUS}" == "FAILED" ]]; then
    break
  fi

  sleep 10  # wait for 10 seconds before checking again
done

echo "Task ${FULL_TASK_NAME} completed with status: ${TASK_STATUS}"