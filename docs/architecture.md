# AriOps Architecture

AriOps uses a modular architecture that separates platform responsibilities, investigation reasoning, and external integrations.

The Software Layer manages requests, incidents, evidence, tools, persistence, and reports. The Agent Layer analyzes available evidence, maintains investigation hypotheses, and produces root cause findings and recommendations. External systems provide infrastructure and observability data through controlled tool integrations.

> This diagram represents the target architecture and will evolve as the project develops.

```mermaid
flowchart TB
    subgraph SOFTWARE["Software Layer"]
        A[Alert / User Request]
        B[Input Interface]
        C[Incident Service]
        D[Incident Repository]
        E[(Persistent Storage)]
        F[Tool Registry]
        G[Evidence Store]
        H[Report Generator]
        V[Service Catalog]

        A --> B
        B --> C
        C --> D
        D --> E
        C --> G
        C --> H
        C --> V
    end

    subgraph AGENT["Agent Layer"]
        I[Initialize Investigation]
        J[Analyze Current Evidence]
        K[Build or Update Hypotheses]
        L{Enough Evidence?}
        M[Select Next Tool]
        N[Identify Root Cause]
        O[Generate Recommendations]

        I --> J
        J --> K
        K --> L
        L -- No --> M
        L -- Yes --> N
        N --> O
    end

    subgraph SYSTEMS["External Systems"]
        P[Infrastructure State]
        Q[Metrics]
        R[Logs]
        S[Traces]
        T[Deployment State]
        U[Source Code and Changes]
    end

    V --> C
    C --> I
    M --> F

    F --> P
    F --> Q
    F --> R
    F --> S
    F --> T
    F --> U

    P --> G
    Q --> G
    R --> G
    S --> G
    T --> G
    U --> G

    G --> J
    O --> C
```

The agent does not directly access infrastructure or persistent storage. External access is performed through controlled tools, while incident state and evidence remain managed by the Software Layer.
