# Geoapify Live Validation

This gate validates the real Geoapify provider with a deliberately small, manual sample. It is
separate from normal CI because it requires a paid/external credential and live network access.

## Credential

Configure this repository secret in GitHub Actions:

```text
LEADFORGE_GEOAPIFY_API_KEY
```

Never place the key in `.env.example`, workflow inputs, source files, logs, issues, PR comments or
artifacts.

## Workflow

Run **Geoapify Live Validation** manually from GitHub Actions. The workflow:

1. installs the backend;
2. verifies that the secret is present without printing it;
3. runs `python scripts/validate_geoapify.py`;
4. uploads `geoapify-live-validation.json` as a short-lived artifact.

The default sample is intentionally bounded to three local-business queries with at most four
businesses each:

- clínicas de estética — Campinas/SP;
- dentistas — Jundiaí/SP;
- academias — Sorocaba/SP.

Each result can cause one Place Details request, so the maximum expected request volume is small
and explicit.

## Report

The report records:

- successful and failed query counts;
- total businesses returned;
- website and phone presence coverage;
- average and maximum latency;
- estimated API request count;
- public business name/category/external ID for sanity checking;
- provider failures with sanitized error messages.

It does **not** export website URLs, phone values, the API key, or the provider's raw payload.

## Pass semantics

`provider_health_passed=true` means all sample queries completed without provider errors and at
least one business was returned overall.

Coverage percentages are measurements, not hard-coded quality gates. A three-query smoke sample
is useful for provider health and rough coverage, but it is not proof of production recall,
accuracy, cost efficiency, or SLA reliability.

If the provider health gate fails, inspect the workflow logs and artifact before changing timeouts,
query behavior or provider selection. Do not hide external failures by returning an empty result.
