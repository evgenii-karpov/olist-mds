# Proposed `lab.py` Command Surface

The exact parser library is implementation-specific; command meaning is normative.

```text
lab.py doctor

lab.py local up
lab.py local down
lab.py local streaming start|status|stop
lab.py local serving run
lab.py local reset-data --force

lab.py gcp preflight
lab.py gcp terraform init|plan|apply|output
lab.py gcp up
lab.py gcp down
lab.py gcp migrate status|apply
lab.py gcp streaming start|status|stop
lab.py gcp vertical-slice run|report
lab.py gcp serving run [--sync-run-seq ...]
lab.py gcp reset-data --force
lab.py gcp destroy --force
lab.py gcp inventory

lab.py parity run
lab.py parity report
```

## Behavioral rules

- `local` commands require no GCP configuration.
- `gcp` commands validate project ID, ADC role, region, Terraform state, and billing preflight.
- `up` does not imply `streaming start`.
- destructive commands require `--force` and print the exact scope.
- parity manages sequential contour operation and prevents overlapping profiles.
