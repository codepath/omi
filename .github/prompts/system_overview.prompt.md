---
mode: agent
---
Look for the lifecycle documentation files, and trace through the flow to create a system architecture document that shows the major actors and their relationships.

## Goal
Identify the heavyweight components/services where most logic lives, show how they're wired together, and indicate key technologies used.

## Structure

### 1. System Overview Diagram (Mermaid)
- Show 5-10 major actors (components/services that do the heavy lifting)
- Wire them together with labeled arrows showing data/control flow
- Use subgrouping to show deployment boundaries (processes, machines, external services)
- Color-code or annotate with key technologies

### 2. Component Catalog (Table)
For each major actor:
- **Component Name** 
- **Technology/Framework** (e.g., "React + MUI", "Node.js custom", "FastAPI")
- **Primary Responsibility** (one sentence)
- **Key Files** (2-3 main files)
- **Heavy Logic** (what complex operations happen here?)

### 3. Technology Stack (Quick Reference)
List the key technologies by layer:
- UI Layer: [technologies]
- State/Logic Layer: [technologies]
- Service/API Layer: [technologies]
- Data Layer: [technologies]
- External Dependencies: [services/APIs]

### 4. Integration Points
Show how major actors communicate:
- Protocol (HTTP, IPC, WebSocket, etc.)
- Data format (JSON, protobuf, etc.)
- Sync vs Async

### 5. Where to Start
- "To understand user interactions, read: [lifecycle docs]"
- "To understand data flow, start with: [component]"
- "To understand business logic, start with: [component]"

## Guidelines
- Focus on "major actors" - components where significant logic lives
- Exclude simple pass-through components, thin wrappers, pure UI components
- Maximum 10 major actors (force prioritization)
- The diagram should fit on one screen
- Each actor should be substantial enough to deserve documentation
- This is a companion to lifecycle documents, not a replacement

## Example Major Actors (not minor ones)
✅ API Gateway with routing logic
✅ Authentication service with token management
✅ State management layer with complex sync logic
✅ Background job processor
✅ Real-time event handler

❌ Simple React component that just renders props
❌ Utility function file
❌ Thin HTTP client wrapper
❌ Config file

The test: "If this component disappeared, would significant logic need to be rewritten?" If no, it's not a major actor.