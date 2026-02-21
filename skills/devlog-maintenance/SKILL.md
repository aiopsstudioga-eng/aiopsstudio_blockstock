---
name: devlog-maintenance
description: "Automatically updates devlog.md after implementing new code or major fixes."
---

# Devlog Maintenance Skill

## Overview

This skill ensures that all significant code changes, feature implementations, and bug fixes are properly documented in the project's `devlog.md` file. It maintains a historical record of technical decisions and progress for the AIOps Studio - Inventory system.

## When to Use This Skill

- Use after completing a feature implementation.
- Use after applying a critical bug fix.
- Use after a significant refactoring effort.
- Use whenever the user explicitly asks for a progress update.
- **Trigger:** This skill should be activated at the end of every successful task execution phase.

## Core Instructions

### 1. Locate devlog.md

The project's primary development log is located at:
`d:\Dev\GitHub\aiopsstudio_blockstock\aiopsstudio_blockstock\devlog.md`

### 2. Format the Entry

Create a new entry at the TOP of the "Development Entries" section (below the headers and format description). Use the following template:

```markdown
### YYYY-MM-DD | [Brief Title of the Work]

**Phase:** [e.g., Phase 2 Enhancement / Bug Fix / Maintenance]
**Focus:** [The primary area of work, e.g., UI Refinement, Reporting]

#### Accomplishments
- 🚀 **Feature/Fix Name**: Detail what was done.
- 🔧 **Underlying Change**: Describe technical aspects.

#### Technical Decisions
- **Decision Name**: Why this approach was chosen and its implications.

#### Files Changed
- `path/to/file1` — Brief description of changes.
- `path/to/file2` — Brief description of changes.

#### Testing
- Summary of tests run (e.g., "All 55 tests passing ✅", "Verified UI layout on Windows 11").

#### Next Steps
- What should be worked on next.
```

### 3. Maintain Consistency

- Use the standard project emojis for common actions:
  - 🚀 Feature
  - 🐛 Bug Fix
  - 🔧 Refactor/Maintenance
  - 🧪 Testing
  - 🎨 UI/UX
  - 📊 Analytics
  - 💰 Financial/Cost
- Ensure the date is in `YYYY-MM-DD` format.
- Group related accomplishments under bold headers.

## Examples

### Example: Feature Implementation

```markdown
### 2026-02-21 | Purchase Tax Rate Feature implementation

**Phase:** Phase 2 Enhancement
**Focus:** Purchase Intake UX — Tax-Inclusive Cost Tracking

#### Accomplishments
- 💰 **Purchase Dialog — Tax Rate Input**: Added tax rate spinbox and preset combo to UI.
- 📄 **Rounding Strategy Document**: Created `rounding_strategy.md` documenting math logic.

#### Technical Decisions
- **Tax folded at UI layer**: Applied tax before service call to keep database schema clean.

#### Files Changed
- `src/ui/intake_dialogs.py` — Added tax UI components.
- `rounding_strategy.md` — New documentation.

#### Testing
- All 18 tests passing ✅. Manual verify of tax calculation logic.
```

## Best Practices

- ✅ **Be Proactive**: Don't wait for the user to ask; update the log as you finish the task.
- ✅ **Be Precise**: Use file paths and specific function names when relevant.
- ✅ **Be Concise**: Focus on the *what* and the *why*, not every single line of code.
- ❌ **Don't Over-Document**: Small typo fixes or minor documentation updates don't always need a devlog entry.
- ❌ **Avoid Vague Titles**: "Updated code" is bad; "Implemented SKU Autocomplete" is good.
