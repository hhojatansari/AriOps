# Investigation Flow

An investigation begins when AriOps receives an alert or a manual request.

The platform creates an incident and starts the investigation workflow. The agent analyzes the available context, creates possible hypotheses, and requests additional evidence through controlled tools when necessary. The process continues until enough evidence is available to produce a root cause and recommendations.

> This diagram represents the target investigation flow and will evolve as the project develops.

```mermaid
sequenceDiagram
    autonumber

    participant S as Alert Source / User
    participant I as Input Interface
    participant M as Incident Service
    participant C as Service Catalog
    participant A as Investigation Agent
    participant T as Tool Registry
    participant X as External Systems
    participant E as Evidence Store
    participant R as Report Generator
    participant D as Persistent Storage

    S->>I: Send alert or investigation request
    I->>M: Validate and normalize input

    M->>C: Resolve registered service targets
    C-->>M: Return cluster, namespace and deployment target
    M->>D: Create incident
    M->>A: Start investigation

    A->>E: Load current evidence
    E-->>A: Return available evidence

    A->>A: Build initial hypotheses
    A->>A: Select next investigation tool

    loop Until enough evidence is collected
        A->>T: Request tool execution
        T->>X: Query external system
        X-->>T: Return result
        T->>E: Store structured evidence
        E->>D: Persist evidence
        E-->>A: Return new evidence

        A->>A: Analyze evidence
        A->>A: Update hypotheses and confidence
        A->>A: Decide whether more evidence is needed
    end

    A->>A: Identify most likely root cause
    A->>A: Generate recommendations
    A-->>M: Return investigation result

    M->>R: Generate report
    R->>D: Store report
    R-->>M: Return completed report

    M-->>I: Return investigation result
    I-->>S: Root cause, confidence and recommendations
```

The initial AriOps scope focuses on investigation and recommendation. Automated remediation is outside the initial MVP.
