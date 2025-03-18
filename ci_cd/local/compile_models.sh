cd ../..
python compile_rule.py models/sales.yaml compiled dev
python compile_rule.py models/users.yaml compiled dev
python compile_rule.py models/event.yaml compiled dev

if [ -f "$PWD/env/demo.env" ]; then
  echo "--- Load $PWD/env/demo.env ---"
  export $(grep -v '^#' "$PWD/env/demo.env" | xargs)
fi
echo "--- Deploying rules to the rules bucket $USER_CLOUDDQ_YAML_CONFIGS_GCS_PATH ---"
gsutil -o "GSUtil:parallel_process_count=1" -m rsync -r -d "compiled/models" "$USER_CLOUDDQ_YAML_CONFIGS_GCS_PATH"
