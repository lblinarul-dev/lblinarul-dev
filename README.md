<h1 align="center">Hi there, I'm Lblinarul 👋</h1>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=58A6FF&center=true&vCenter=true&width=560&lines=Building+things+that+ship;Always+learning%2C+always+shipping;Senior+Full-Stack+Development" alt="Typing SVG" />
</p>

<p align="center">
  <a href="https://github.com/lblinarul-dev">
    <img src="https://img.shields.io/github/followers/lblinarul-dev?label=Follow&style=social" alt="GitHub followers" />
  </a>
  <img src="https://komarev.com/ghpvc/?username=lblinarul-dev&label=Profile%20Views&color=58A6FF&style=flat" alt="Profile views" />
</p>

---

## 👨‍💻 Senior Full-Stack Developer

**React · TypeScript · Python · FastAPI**

I build and maintain full-stack web applications across frontend, backend, data, and delivery. My focus is on practical engineering: clear architecture, reliable APIs, maintainable code, automated testing, and production-ready development workflows.

I enjoy solving problems where product requirements meet technical constraints — from responsive React interfaces and API design to database performance, debugging, CI/CD, and incremental system improvement.

---

## 🎯 Core Expertise

**Frontend** — React, TypeScript, JavaScript, Next.js, component architecture, responsive UI

**Backend** — Python, FastAPI, Django, REST APIs, authentication, authorization, asynchronous processing

**Data** — PostgreSQL, SQL, Redis, database design, migrations, indexing, query optimization

**Delivery / DevOps** — Docker, GitHub Actions, CI/CD, Linux, Git/GitHub workflows

**Quality** — pytest, Jest, Playwright, unit testing, integration testing, end-to-end testing, code review

---

## 🌱 Mentoring Junior & New Programmers

I answer questions and give code-level feedback to people earlier in their engineering path. I keep it practical — the goal is to help someone understand the underlying problem and become able to solve the next one independently.

**How I help:**

- Explain why something does not work, not only how to patch it
- Review junior-written code with specific, actionable feedback
- Walk through debugging by isolating failures before applying fixes
- Explain architectural and implementation trade-offs
- Point toward the next concept worth learning based on the actual problem

If you're a junior developer with a question, feel free to open a [Discussion](https://github.com/lblinarul-dev/lblinarul-dev/discussions) on this repository.

---

## 📐 Math Mentoring for Students

I tutor students in higher mathematics, with an emphasis on understanding concepts and connecting abstract ideas to practical applications in software and engineering where useful.

**Areas I cover:**

- Calculus (single and multivariable)
- Linear algebra
- Discrete mathematics
- Probability & statistics
- Introductory algorithm analysis / complexity

**Approach:**

- Work from the student's actual coursework or problem set
- Emphasize why a method works before mechanical repetition
- Use small code examples or visualizations when they make abstract concepts easier to understand

---

## 🔍 Open-Source Code Review & Issue Fixing

I review other people's GitHub projects and contribute fixes, mostly working from issue trackers: reproducing a reported problem, narrowing down the root cause, and submitting or reviewing changes that fit the project's existing conventions.

**What this typically looks like:**

- Reproduce issues locally and confirm the actual root cause
- Submit PRs with a clear explanation of the problem, fix, and verification
- Review code for correctness, edge cases, and maintainability
- Follow existing project conventions and test setups rather than imposing unnecessary changes

### Recent GitHub activity

<!-- EXTERNAL-CONTRIBUTIONS:START -->
| Repo | Type | Description | Link |
|---|---|---|---|
| lblinarul-dev/interactiv-dashboard-readme-gemini | Project | interactiv-dashboard-readme-gemini | [Repo](https://github.com/lblinarul-dev/interactiv-dashboard-readme-gemini) |
| lblinarul-dev/react-debugger | Project | I Fixed a Production-Style React Performance Problem | [Repo](https://github.com/lblinarul-dev/react-debugger) |
<!-- EXTERNAL-CONTRIBUTIONS:END -->

> This table is updated automatically from real public GitHub contribution activity and contains work in repositories I do not own.

---

## 📁 My Repositories

<!-- OWN-PROJECTS:START -->
| Repo | Description | Last Updated | Link |
|---|---|---|---|
| react-debugger | I Fixed a Production-Style React Performance Problem | 2026-09-07 | [Repo](https://github.com/lblinarul-dev/react-debugger) |
<!-- OWN-PROJECTS:END -->

### Selected Work — `react-debugger`

**Project:** [lblinarul-dev/react-debugger](https://github.com/lblinarul-dev/react-debugger)

**Problem** — A production-style debugging case in `backend/services.py` contained an async `upload_to_imgbb()` function that was defined inside `generate_image()` but never called. The surrounding comment claimed images were uploaded to ImgBB, while the implementation returned the temporary DALL-E URL directly.

**Decision** — Trace the actual execution path before changing unrelated code. The fix implemented the intended upload path: generate the image, download its bytes, call the ImgBB upload helper, return the ImgBB URL when successful, and retain the DALL-E URL as a fallback when the upload cannot be completed.

**Result** — Source-level verification confirmed that `_upload_to_imgbb()` exists and is called by `generate_image()`. An upload test also exercised the error path; the recorded test used an invalid/revoked API key, so live ImgBB hosting requires a valid key.

This project is listed here as **my own project**. It is intentionally not represented as an external contribution.

---

## 🏗️ Engineering Focus

- **API Architecture** — REST design, OpenAPI documentation, validation, authentication, authorization, and clear service boundaries
- **Performance** — profiling, database query optimization, indexing, caching, and efficient data access
- **Testing** — pytest, Jest, Playwright; unit, integration, and end-to-end testing
- **Security** — input validation, authentication/session handling, dependency hygiene, and secure API boundaries
- **Maintainability** — TypeScript/Python typing, modular architecture, readable interfaces, documentation, and incremental refactoring
- **Delivery** — reproducible development environments, CI checks, automated testing, and deployment workflows
- **Debugging** — isolate reproducible failures, inspect system behavior, identify root causes, and make targeted fixes

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=js,ts,react,nodejs,python,git,github,vscode" alt="JavaScript, TypeScript, React, Node.js, Python, Git, GitHub and VS Code" />
</p>

**Primary**

`React` `TypeScript` `Python` `FastAPI` `PostgreSQL` `REST APIs` `Docker` `CI/CD`

**Supporting**

`Next.js` `Django` `Redis` `GitHub Actions` `Playwright` `pytest` `Jest` `SQLAlchemy`

---



<a id="-github-activity" name="-github-activity"></a>

## 📊 GitHub Activity

> These cards are live GitHub-derived images and may be cached by the services that generate them.

<table align="center">
  <tr>
    <td>
      <img src="https://github-readme-stats.vercel.app/api?username=lblinarul-dev&show_icons=true&theme=tokyonight&hide_border=true&v=2026091106" alt="GitHub Stats" />
    </td>
    <td>
      <img src="https://streak-stats.demolab.com/?user=lblinarul-dev&theme=tokyonight&hide_border=true&v=2026091106" alt="GitHub Streak" />
    </td>
  </tr>
</table>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=lblinarul-dev&layout=compact&theme=tokyonight&hide_border=true&v=2026091106" alt="Top Languages" />
</p>

### 📈 Activity — last 90 days

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=lblinarul-dev&days=90&theme=tokyo-night&hide_border=true&bg_color=00000000&custom_title=Contribution+Activity+%28Last+90+Days%29&v=2026091106" alt="GitHub activity graph for the last 90 days" />
</p>

### 🐍 Contribution Activity

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/lblinarul-dev/lblinarul-dev/main/assets/github-contribution-grid-snake-dark.svg?v=2026091106">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/lblinarul-dev/lblinarul-dev/main/assets/github-contribution-grid-snake.svg?v=2026091106">
    <img alt="GitHub contribution snake" src="https://raw.githubusercontent.com/lblinarul-dev/lblinarul-dev/main/assets/github-contribution-grid-snake.svg?v=2026091106">
  </picture>
</p>

---

## 🔧 Development Approach

- Start with the simplest architecture that satisfies the real requirements.
- Keep frontend, backend, and data responsibilities clear.
- Prefer explicit API contracts and predictable failure handling.
- Test business-critical behavior and regression-prone areas.
- Measure before optimizing performance.
- Automate repetitive quality and delivery checks.
- Refactor incrementally instead of introducing unnecessary complexity.
- Treat security, accessibility, reliability, and maintainability as part of normal development.
- Document important technical decisions so systems remain understandable as they evolve.

---

## 📫 Contact

[LinkedIn](https://linkedin.com/in/YOUR_HANDLE) · [Email](mailto:you@example.com)

Junior developers with questions, or maintainers who want a hand triaging issues, can open a [Discussion](https://github.com/lblinarul-dev/lblinarul-dev/discussions).
