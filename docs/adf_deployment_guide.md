# ADF deployment guide

ADF definitions can't be run by a reviewer, so this repo documents heavily.
These are the steps to deploy to your own Azure subscription.

## 1. Create resources

- Azure Data Factory (V2), an Azure Blob Storage account, and an Azure Key Vault.
- Grant the ADF managed identity `Key Vault Secrets User` on the vault.

## 2. Store secrets in Key Vault

Add these secrets (names must match the linked-service references):

| Secret name | Value |
|---|---|
| `snowflake-password` | Snowflake user password |
| `blob-connection-string` | Blob storage connection string |

## 3. Parameterize the linked services

In the ADF Studio UI, import `linked_services/*.json` and replace the
`YOUR_*` default parameter values with your own — or better, pass them from
the deployment pipeline. Never commit real values back to this repo.

## 4. Import datasets and pipelines

Import `datasets/*.json`, then `pipelines/*.json`. Publish.

## 5. Validate

Run `python -m pytest tests/ -q` in this repo first (validates JSON shape,
references, retry policies, and no hardcoded secrets). Then trigger
`pl_data_quality_gate` manually and confirm a green run before scheduling.

## 6. Schedule

Add a tumbling-window or schedule trigger on `pl_data_quality_gate` for the
nightly run; the gold refresh executes downstream on the success path.
