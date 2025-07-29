<gsl-template type="manual" trace_id="YYYYMMDDTHHMMSS±HHMM">
<gsl-header>

# Grit Labs Manual Task Template
</gsl-header>

<gsl-block>
<gsl-label>

## Objective:
</gsl-label>
<gsl-description>

Define tasks or actions that are entirely manual, non-automatable, and performed outside the agent's observable context.

</gsl-description>

<gsl-label>

## Tasks:
</gsl-label>
<gsl-tasks>

<gsl-task>
<gsl-title>Rename GitHub repo to OLD_[repo-name]</gsl-title>
<gsl-note>Performed manually via GitHub UI; outside automation scope.</gsl-note>
</gsl-task>

<gsl-task>
<gsl-title>Physically install network cables in server room</gsl-title>
<gsl-note>Human action requiring physical presence.</gsl-note>
</gsl-task>

<!-- Additional tasks as needed -->

</gsl-tasks>

<gsl-label>

## Notes:
</gsl-label>
<gsl-description>

These tasks are deliberately outside the system's visibility or automation capabilities. Their documentation here provides holistic traceability for the entire project scope.

</gsl-description>
</gsl-block>

<gsl-template-guide>

## 📌 How This Template Works

This is a **non-executable, human-only** template type (`manual`). It is distinct from other templates (like `project-plan`) because:

- Agents **cannot execute or validate** the tasks listed here.
- Tasks listed are performed entirely by humans, often involving external or physical actions not visible at the repository or system level.
- This document exists solely to provide context, audibility, and traceability for work that is manual, external, or out-of-band.

When filling out this template, provide clear, descriptive tasks and notes. After completion and commitment to the repository, remove this `<gsl-template-guide>` section.

</gsl-template-guide>
</gsl-template>
