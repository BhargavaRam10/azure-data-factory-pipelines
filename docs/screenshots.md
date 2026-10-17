# Screenshots to capture

ADF can't be executed by a reviewer, so screenshots are the proof of work.
Capture these in ADF Studio after deploying (see `adf_deployment_guide.md`)
and add the images to this folder:

1. **Pipeline canvas — `pl_ingest_apis`**: Lookup → SetVariable → Copy → Script,
   with the watermark variable visible.
2. **Pipeline canvas — `pl_data_quality_gate`**: Lookup → IfCondition, with the
   false branch (Web activity → Fail) expanded.
3. **A successful Monitor run** of `pl_data_quality_gate` showing all green.
4. **A failed quality-gate run** (temporarily break a rule) showing the alert
   activity firing and the pipeline marked failed — this is the behavior that
   protects gold from bad data.
5. **Linked service test connection** for `ls_snowflake` (mask credentials).
