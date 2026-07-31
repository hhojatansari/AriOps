# Kubernetes Integration

AriOps uses the official Kubernetes Python client for read-only investigation
tool calls. The current adapter implements pod, pod-log, event, and deployment
queries behind the existing controlled tool contracts.

## Required configuration

| Setting | Purpose |
| --- | --- |
| `ARIOPS_KUBERNETES_TOOL_ADAPTER` | `real` uses the Kubernetes API; `fake` is for local demos and tests. |
| `ARIOPS_KUBERNETES_CONNECTION_MODE` | `kubeconfig` for an external kubeconfig or `in_cluster` for a ServiceAccount. |
| `ARIOPS_KUBERNETES_CLUSTER_NAME` | Name used to match registered service deployments to this Kubernetes connection. |
| `ARIOPS_KUBERNETES_KUBECONFIG_PATH` | Optional kubeconfig path; empty uses the default location. |
| `ARIOPS_KUBERNETES_ALLOWED_NAMESPACES` | Comma-separated namespace allowlist; use `*` for every namespace. Empty denies all reads. |
| `ARIOPS_KUBERNETES_REQUEST_TIMEOUT_SECONDS` | Timeout for each Kubernetes API request. |
| `ARIOPS_KUBERNETES_MAX_LOG_TAIL_LINES` | Upper bound on the number of log lines AriOps can request. |

## Read-only access

The adapter only calls Kubernetes `get` and `list` API operations. The required
RBAC permissions are `get` and `list` for pods, deployments, and events, plus
`get` for the `pods/log` subresource. It does not create, update, patch, or
delete Kubernetes resources.

For local kubeconfig access, the process running AriOps must be able to read
the kubeconfig file and reach the configured control-plane endpoint. For
in-cluster access, use a dedicated ServiceAccount with the minimum RBAC scope.
