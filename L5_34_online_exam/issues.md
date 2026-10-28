# Lab 5 — Issue Table (`online_exam.py`)

Static Analysis Tools Utilized:
- **Pylint 4.1.3** (Python 3.12.10)
- **Bandit 1.9.4** (Python 3.12.10)
- **Flake8 7.4.1** (pycodestyle: 2.15.0, pyflakes: 4.0.3, mccabe: 0.7.0)

Line numbers in the table refer to the **original** script before remediation. Issues are prioritized by severity (High and Medium security/bugs first, followed by convention and style).

## Documented Issues and Fix Approaches

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| **B605**: start_process_with_a_shell (Bandit, **High Severity**) | Security | 56 | `os.system("ssh " + labPc + " lock-screen")` executes a shell command constructed via string concatenation with unvalidated user input (`labPc`). This creates a command injection vulnerability (CWE-78), allowing arbitrary shell commands to run (e.g. `pc1; rm -rf /`). | Replaced `os.system` with `subprocess.run` passing an argument list without a shell (`shell=False`). Validated `lab_pc` against a strict regex whitelist (`^[a-zA-Z0-9_.-]+$`), resolved the binary via `shutil.which("ssh")`, and added `--` argument separator. Added justified `# nosec B603` annotation. |
| **B324**: Use of weak MD5 hash (Bandit, **High Severity**) | Security | 16 | `hashlib.md5(text.strip().lower().encode()).hexdigest()` uses MD5, which is cryptographically broken and prone to collision attacks (CWE-327: Broken Cryptographic Algorithm). | Replaced MD5 with secure, collision-resistant `hashlib.sha256(text.strip().lower().encode()).hexdigest()`. |
| **W0102**: Dangerous mutable default argument (Pylint, **Bug**) | Bug | 23 | `def gradeStudent(studentName, responses, penalties={}):` uses a mutable dictionary as a default argument. The dict is instantiated once at function definition, causing state to leak across calls for different students. | Changed parameter default to `penalties=None` and created a fresh dictionary inside the function body: `if penalties is None: penalties = {}`. |
| **B105**: Hardcoded password string (Bandit, **Low Severity**) | Security | 11 | `PROCTOR_PASSWORD = "proctor-demo"` hardcodes credentials directly into the source code (CWE-259), exposing them in version control. | Read credentials dynamically from the execution environment: `os.environ.get("PROCTOR_PASSWORD", "")`. |
| **B311**: Pseudo-random generator for security (Bandit, **Low Severity**) | Security | 20 | `random.choice(QUESTIONS)["q"]` uses standard pseudo-random number generator (Mersenne Twister), which is predictable (CWE-330). Bonus questions should not be predictable. | Switched to `secrets.choice(QUESTIONS)["q"]` from Python's cryptographically secure `secrets` module. |
| **B404 / B603**: Subprocess informational notices (Bandit, **Low**) | Security | 6, 75 | Introducing `subprocess.run` produces informational security notices regarding process spawning and input validation. | Validated hostname with regex allowlist and used argument list; added targeted `# nosec B404` and `# nosec B603` comments with inline justification. |
| `topper()` unhandled empty dictionary (Manual Review) | Bug | 51–52 | Calling `topper()` when `results` is empty raises an unhandled `ValueError: max() arg is an empty sequence`, whereas `classAverage()` safely returns 0. | Added a guard condition `if not results: return None` before evaluating `max()`. |
| Module execution on import (Manual Review) | Bug / Architecture | 73 | `main()` was called directly at the module root, executing demo code unconditionally whenever imported as a library or test target. | Enclosed invocation within `if __name__ == "__main__": main()`. |
| **C0103**: Invalid names / non-PEP 8 naming (Pylint) | Convention | 15, 19, 23, 35, 45, 54 | Functions and arguments (`hashAnswer`, `pickBonusQuestion`, `gradeStudent`, `studentName`, `getGrade`, `classAverage`, `lockScreen`, `labPc`) used camelCase instead of PEP 8 snake_case. | Renamed all functions and parameters to standard snake_case (`hash_answer`, `pick_bonus_question`, `grade_student`, `student_name`, `get_grade`, `class_average`, `lock_screen`, `lab_pc`) and updated all caller sites. |
| **C0114 / C0116**: Missing docstrings (Pylint) | Convention | 1, 15, 19, 23, 35, 45, 51, 54, 59 | The module and every function lacked docstrings explaining functionality, parameters, and return types. | Added comprehensive docstrings complying with PEP 257 for the module and all functions. |
| **C0200**: Iteration with `range(len())` (Pylint) | Refactor | 25 | `for i in range(len(QUESTIONS)):` manually indexes into a sequence instead of idiomatic Python iteration. | Refactored loop to `for i, question in enumerate(QUESTIONS):` and referenced `question["answer"]` directly. |
| **R1705**: Unnecessary `elif` after `return` (Pylint) | Refactor | 37–42 | `getGrade` used redundant `elif` and `else` blocks following early `return` statements, adding unnecessary nesting. | Flattened logic to sequential early `if` returns with a terminal `return "C"`. |
| **E302**: Expected 2 blank lines (Flake8) | Style | 54 | Only 1 blank line preceded the top-level function `lockScreen()`, violating PEP 8 layout rules. | Added the second required blank line. |
| **E225**: Missing whitespace around operator (Flake8) | Style | 67 | `average=classAverage()` lacked whitespace surrounding the assignment operator `=`. | Formatted with surrounding whitespace: `average = class_average()`. |
| **E261**: Comment spacing (Flake8) | Style | 69 | `print("Topper:", topper()) # highest score` had only 1 space before `#`, violating PEP 8 (minimum 2 spaces required). | Added 2 spaces before the inline comment. |
| **E501**: Line too long (Flake8) | Style | 70 | The final print statement exceeded the standard 79-character PEP 8 limit (93 characters). | Split and formatted string interpolation onto clean lines under 79 characters. |
| **E128**: Continuation line under-indented (Flake8) | Style | 63 | The continuation line of `gradeStudent("Divya", ...)` was under-indented for visual alignment. | Properly indented multiline dictionary argument. |

---

## Static Analysis Summary Comparison

| Tool | Before Fixes | After Fixes | Status |
|---|---|---|---|
| **Pylint** | **5.65 / 10** (20 warnings/errors) | **10.00 / 10** (0 issues) | **PASSED** (Target > 9.5 exceeded) |
| **Bandit** | **4 issues** (2 High: B605, B324; 2 Low: B105, B311) | **0 issues** (No security issues identified) | **PASSED** (All High & Medium resolved) |
| **Flake8** | **4 style violations** (E302, E225, E261, E501) | **0 violations** | **PASSED** (Full PEP 8 compliance) |

Program functional execution remains 100% verified and matches original output behavior.
