---
mode: agent
---
# Trace the lifecycle of a use case

I’m a junior developer onboarding onto a new codebase, and I think the best way to ramp up is to follow the lifecycle of a use case. Generate a cheatsheet of the lifecycle, using the guidelines below.

Structure:
- Title with use case name and user story
- Layer 1: Simple Mermaid flowchart showing user journey (6-8 steps max)
- Layer 2: Mermaid component architecture diagram showing UI/State/Service/External layers with data flow arrows, plus a table mapping each component to its actual implementation (function/class name, file:line)
- Layer 3: Mermaid sequence diagram showing the detailed interaction flow, followed by 2-3 key design patterns used
- Data Structures: TypeScript interfaces/types with inline comments
- Quick Reference: Bullet points of practical info (event triggers, formats, error handling)
- Related Lifecycles: List 3-5 related use case traces

Component Overview
- List the key components and services with their roles

Guidelines:
- Use Mermaid for all diagrams
- Add actual key classnames, as appropriate 
- Focus on visual understanding, not verbose explanations
- Include file paths and line numbers in tables
- NO code duplication (reference files instead)

Output lifecycle into a file like “/memory/system/001_lifecycle_xxx_xxx_xxx.md”