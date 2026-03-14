param(
  [string]$Config = "configs/default.json"
)

python scripts/run_reproduce.py --config $Config
