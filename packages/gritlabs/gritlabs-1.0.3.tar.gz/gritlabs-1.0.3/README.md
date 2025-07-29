# Grit Labs

> ⚠️ **Work in Progress**: This package is currently in active development and **not production-ready**. Expect breaking changes, incomplete features, and possible instability. Feedback is welcome!

Grit Labs is a Prompt Management and Traceability Tool designed to help teams easily create, organize, track, and validate structured prompts used for documentation, automation, and AI-driven workflows.

---

## ✨ Why Grit Labs?

Unlike traditional project management or tracking tools, Grit Labs Prompts are natively readable by AI agents, including ChatGPT Codex. Because each Prompt is structured Markdown combined with embedded XML, there's no need for complex middleware or API integrations. Codex Agents directly understand your requirements, immediately execute instructions, and automatically maintain perfect traceability.

This makes Grit Labs uniquely powerful for modern AI-driven workflows, ensuring rapid iteration, precise compliance, and effortless auditability.

---

## 🚀 Features

* ✅ File-safe, timezone-aware **Trace IDs** (e.g., `20250720T154500+0000`)
* ✅ Human-readable Markdown + structured **Grit Structured Language (GSL)** XML blocks
* ✅ Deterministic file paths for each artifact
* ✅ CLI-based template generation, validation, and reporting
* ✅ Designed around ChatGPT Codex 2025
* ✅ **Project audibility and engineering traceability**

---

## 🌐 Framework Compatibility

Grit Labs is completely decoupled and works with popular host technologies, including:

* ✅ **.NET / C#** (via NuGet)
* ✅ **Angular**, **React**, **Node.js** (via npm)
* ✅ Shell environments, CI/CD pipelines, or standalone projects

Pin the version in your project’s package file (`.csproj`, `package.json`, etc.). This will ensure consistency, reproducibility, and historical traceability across teams and environments, and prevent unexpected issues due to version discrepancies.



---

## 🗝 Getting Started

### 1. Install Python (≥ 3.7)

Make sure `python3` is installed.

### 2. Add Grit Labs to your project

#### 🔹 For npm-based projects:

```bash
npm install --save-dev gritlabs
```

#### 🔹 For Python projects (this repo):

```bash
pip install -e .
```

#### 🔹 For .NET projects:

```xml
<PackageReference Include="GritLabs" Version="1.0.0" PrivateAssets="all" />
```

### 3. Generate a template

```bash
npx gritlabs template generate feature
```
Use `-o` to specify a custom destination path:

```bash
npx gritlabs template generate feature -o my_feature.md
```

### 4. Validate all templates

```bash
npx gritlabs validate-all
```

### 5. Generate a Trace ID

```bash
gritlabs generate trace_id
```

### 6. Manage configuration lists

```bash
gritlabs ncc add abcd123 -r "Legacy commit"
gritlabs ncc list
gritlabs ncc remove abcd123

gritlabs inactive add 20250720T123456+0000 -r "Deprecated"
gritlabs inactive list
gritlabs inactive remove 20250720T123456+0000
```

## 📁 Project Structure

```text
gritlabs/   Python package with CLI code, templates, and XML data
tests/      Unit tests
prompts/    GSL prompt templates
```


---

## 🔑 Terms

- **AGENTS.md** — A declarative registry of agents, constraints, and setup rules.
- **Agent** — An AI (e.g., Codex) that interprets and executes the prompt.
- **CLI** — Command-Line Interface for generating, validating, and reporting templates.
- **Deterministic File Path** — Predictable file locations structured by date and Trace ID (`prompts/YYYY/MM/DD/YYYYMMDDTHHMMSS±HHMM.md`).
- **Directive** — A command or goal embedded in the prompt for the agent to follow.
- **GSL (Grit Structured Language)** — Embedded XML dialect used in Grit Labs templates, supporting structured validation and machine parsing.
- **ignore:** — A commit message tag indicating a trivial or non-traceable change (e.g., typo fix, formatting) that is intentionally excluded from Trace ID validation and audit processes.
- **inactive-prompts.xml** — Lists prompts excluded from validation and reporting, with reasons for exclusion.
- **non-conforming-commits.xml** — Lists Git commits intentionally excluded from Trace ID validation.
- **Prompt** — A Markdown + GSL file created from a template; defines a unit of intent or instruction.
- **template-types.xml** — Defines allowed template types recognized by Grit Labs, ensuring template consistency.
- **Trace ID** — A unique, timezone-aware identifier in the format `YYYYMMDDTHHMMSS±HHMM`.


---

## 🧭 How It Works

Grit Labs supports a structured, traceable, and AI-assisted workflow:

1. **Generate a Prompt Template**

   ```bash
   gritlabs template generate <type>
   ```

2. **Populate with AI**
   Fill out the template by entering structured information such as the title, description, and acceptance criteria. For example, a `feature` prompt might describe a new capability like profile image uploads. This can happen as part of a natural conversation with ChatGPT, where you progressively refine the prompt's structure and content through back-and-forth exploration.

3. **Store Prompt**
   Save completed prompt:

   ```
   prompts/YYYY/MM/DD/YYYYMMDDTHHMMSS±HHMM.md
   ```

4. **Trigger Codex Agent**
   Execute prompt at given Trace ID.

5. **Codex Executes & Commits**
   Codex runs instructions and commits, tagging with Trace ID.

6. **Pull Request Preparation**
   Optionally opens a pull request referencing the original prompt.

> Grit Labs uses structured configuration files stored in the `data` folder to control validation and reporting behavior:
> 
> -   `inactive-prompts.xml`: Prompts listed here will not appear in validation and reports but maintain historical file traceability.
>     
> -   `template-types.xml`: Defines and constrains allowable prompt template types.
>     
> -   `non-conforming-commits.xml`: Git commits listed here will skip Trace ID validation, helpful for legacy or special commits.
>     


---

## 📁 Template Types

| Type           | Description                                   |
| -------------- | --------------------------------------------- |
| `feature`      | Feature-level requirement                     |
| `fix`          | Bugfix requirement                            |
| `spec`         | Technical or interface specification          |
| `scenario`     | Behavioral narrative / test-like usage        |
| `article`      | Architecture or decision-making documentation |
| `terminology`  | Domain vocabulary reference                   |
| `config`       | Grit Labs system or repo-level settings       |
| `roadmap`      | High-level planning overview                  |
| `project-plan` | Task-level time-based execution schedule      |
| `manual`       | Human-only tasks outside system visibility    |

---

## 💾 Grit Structured Language (GSL)

GSL is an embedded XML dialect inside Grit Labs templates. It defines structured metadata and sections like title, description, criteria, and more.

### ✳️ Why GSL?

* 🔍 **Schema-validatable** via XSD
* 💬 **Human-readable**, inside Markdown
* 📊 **Machine-parsable** for reporting, analysis, and enforcement
* 🔄 Enables clean round-tripping between code, automation, and documentation

---

## 📊 Reporting Examples

```bash
gritlabs report list --type scenario
gritlabs report count --type feature --month 2025-07
gritlabs report list --after 2025-07-13
gritlabs report commits --match trace
```

---

## 🔐 Git Integration

Enforce commits reference a valid Trace ID:

```bash
gritlabs validate-commits --commit-range HEAD~1..HEAD
```

---

## 📜 Audibility & Traceability

Grit Labs provides an audit-ready record:

| Audit Dimension       | Backed By                          |
| --------------------- | ---------------------------------- |
| **What** changed      | Markdown + GSL templates           |
| **Why** it changed    | Explicit `feature`, `fix`, `spec`  |
| **When** it changed   | Trace ID (timestamped filename)    |
| **Who** changed it    | Git commit history                 |
| **Is it valid?**      | Schema validation + CI enforcement |
| **Is it documented?** | Fully version-controlled with code |

Ideal for enterprise teams, regulated environments, and high-trust systems.

### ✅ **Validation Philosophy**

Grit Labs validation centers around a single core conceptual rule:

> **Every commit must reference a valid Trace ID that corresponds to a structured, schema-compliant template.**

While simple to state, this rule encapsulates multiple layers of robust validation—ensuring filenames, directory structures, embedded metadata, commit messages, and template schemas all align. Behind the scenes, Grit Labs applies numerous detailed checks, cross-verifications, and consistency validations to uphold project audibility and traceability.

---

## 📚 Learn More

* `gritlabs template generate <type>` — create a new artifact
* `gritlabs validate-all` — validate all templates and XML
* `gritlabs report` — generate traceability and audit reports
* `gritlabs ncc` — manage non-conforming commit hashes
* `gritlabs inactive` — manage inactive prompts

---

## 📜 License

AGPL — open for individual, team, and enterprise use under a copyleft license.