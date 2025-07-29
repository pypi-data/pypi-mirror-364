<gsl-template type="project-plan" trace_id="YYYYMMDDTHHMMSS±HHMM">
<gsl-header>

# [Project Name or Title Here]
</gsl-header>

<gsl-block>
<gsl-label>

## Title:
</gsl-label>
<gsl-title>
[Short, goal-oriented title for the project plan]
</gsl-title>

<gsl-label>

## Description:
</gsl-label>
<gsl-description>
[One or two paragraphs: What is the purpose of this project plan? What is being delivered? Who is it for? Include any high-level goals or context.]
</gsl-description>

<gsl-label>

## Major Features & Workstreams:
</gsl-label>
<gsl-tasks>

<gsl-task>
<gsl-task-title>[Feature or Workstream Title]</gsl-task-title>
<gsl-note>
- [What does this feature/workstream deliver?]
- [How is it validated, integrated, or tested?]
- [Any dependencies or special requirements?]
</gsl-note>
</gsl-task>

<!-- Add more <gsl-task> blocks as needed for each major feature, fix, or workstream -->

</gsl-tasks>

<gsl-label>

## Sequencing & Milestones:
</gsl-label>
<gsl-description>
[List the key steps in the order you expect to do them, and/or identify major milestones. Use numbers, bullets, or dates as you see fit.]
</gsl-description>

<gsl-label>

## Acceptance Criteria:
</gsl-label>
<gsl-acceptance-criteria>
<gsl-criterion>
[Clear, testable condition for project plan completion]
</gsl-criterion>
<!-- Add more <gsl-criterion> blocks as needed -->
</gsl-acceptance-criteria>
</gsl-block>

<gsl-template-guide>

## 📌 How This Template Works

- This is a feature-driven, immutable snapshot of the project’s intended scope and structure.
- Capture concrete deliverables and criteria for completion—don’t update after creation.
- If scope, intent, or actuals diverge, create a new `project-plan`, `fix`, or `article` to document changes.
- Tasks and acceptance are statements of intent as of the date in the `trace_id`.
- Omit `<gsl-phases>` and `<gsl-milestones>` sections unless you require them for a more waterfall/phase-based approach.

</gsl-template-guide>
</gsl-template>
