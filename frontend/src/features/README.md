# Feature Modules Directory

This folder organizes the platform's core functional modules. Each directory should contain component, hooks, and services scoped entirely to that domain.
- `auth`: user credentials exchange and route guarding
- `dashboard`: main operational views and aggregation panels
- `endpoints`: active hosts list, metadata details, status indicators
- `monitoring`: real-time charts (CPU, RAM, logs)
- `alerts`: system thresholds configuration and events list
- `security`: vulnerabilities scanners, alerts list, process telemetry analyzer
- `compliance`: security baseline checks (SAIF, custom baselines)
- `audit`: actions history logs
- `reports`: PDF export and telemetry summaries engine
- `settings`: global platform toggles and agent key rotations
