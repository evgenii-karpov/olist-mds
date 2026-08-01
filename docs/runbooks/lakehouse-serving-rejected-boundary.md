# Runbook: Lakehouse Serving Rejected Boundary

## 1. Overview
When a CDC transaction contains a rejected row, the transaction status in `audit.mysql_transactions` becomes `REJECTED`.
Serving planner stops publication at the boundary and emits alert `ServingRejectedBoundary`.

## 2. Remediation
1. Inspect rejected rows in `lakehouse.audit.normalization_errors` and `lakehouse.audit.schema_violations`.
2. Perform finite replay correction or fixed payload retry.
3. Re-run `sync-serving`:
```powershell
python scripts/cdc/local_lab.py sync-serving
```
