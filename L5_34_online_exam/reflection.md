# Lab 5 — Reflection: Static Code Analysis

## 1. Which issues were easiest to fix, and which were hardest?

- **Easiest Issues:**
  The easiest issues to address were the syntactic, formatting, and linting violations reported by Flake8 and Pylint. These included adding missing whitespace around assignment operators (`E225`), adding the second space before inline comments (`E261`), inserting the required two blank lines between top-level functions (`E302`), and renaming functions and variables from camelCase to snake_case (`C0103`). These violations had clear, pinpointed line and column numbers with unambiguous remediation paths defined by PEP 8 conventions.

- **Hardest Issues:**
  The most complex issue was remediating the **B605** security vulnerability flagged by Bandit in `lockScreen()`:
  ```python
  os.system("ssh " + labPc + " lock-screen")
  ```
  Simply replacing `os.system` with a naive `subprocess.run` was insufficient because unvalidated external strings passed into subprocess calls can still suffer from argument injection (e.g. host strings beginning with `-o` or `-F` acting as flags rather than hostnames) and path resolution exploits. Solving this properly required making several deliberate architectural security decisions:
  1. Validating the host string against a strict regex whitelist (`^[a-zA-Z0-9_.-]+$`) to reject malicious command chaining and control characters.
  2. Resolving the explicit binary path using `shutil.which("ssh")`.
  3. Passing arguments as a discrete list with `shell=False` to prevent shell interpretation.
  4. Adding the `--` command-line separator before the hostname so flags cannot be injected.
  5. Correctly handling the subsequent informational Bandit notices (**B404** and **B603**) through targeted, justified `# nosec` annotations rather than unsafe global suppression.

---

## 2. Did the tools report any false positives?

None of the tools reported outright false positives in terms of incorrect tool mechanics; however, several findings represented contextual nuances:
- **Bandit B105 (`PROCTOR_PASSWORD = "proctor-demo"`):**
  In the context of an academic demo script, `"proctor-demo"` was a dummy placeholder string rather than a production credential. However, Bandit rightly flags hardcoded credential variables because committing secret strings into version control is a hazardous pattern in real-world systems. Moving it to an environment variable (`os.environ.get("PROCTOR_PASSWORD", "")`) enforced good security hygiene.
- **Bandit B311 (`random.choice`):**
  Standard pseudo-random generation is fine for non-sensitive simulations, but for an examination setting, predictable bonus question selection can be exploited if seeds are known. Replacing it with `secrets.choice()` is objectively better practice.
- **Bandit B404 / B603 on `subprocess`:**
  Once `subprocess.run` was safely parameterized without a shell and with strict input sanitization, Bandit still emitted Low-severity informational warnings. These are not vulnerabilities per se, but reminders to verify input safety. Using specific `# nosec B404` and `# nosec B603` inline comments with written explanations correctly documented that the call had been audited and made safe.
- **Blind spots (False Negatives):**
  Crucially, static analysis tools did not catch two logical/runtime bugs:
  1. `topper()` called `max(results, key=results.get)` directly without checking if `results` was empty, causing a runtime `ValueError: max() arg is an empty sequence`.
  2. `main()` was executed at module load time rather than guarded behind `if __name__ == "__main__":`.
  This demonstrated that static analysis tools are powerful supplements to, but never complete replacements for, thorough manual code review and automated unit testing.

---

## 3. How would you integrate these tools into a real development workflow?

To maintain clean and secure code in production, static analysis tools should be integrated across multiple tiers of the software development lifecycle (SDLC):

1. **Local Developer Pre-Commit Hooks (Git Hooks):**
   - Use `pre-commit` to execute fast tools like **Flake8** and **Bandit** automatically prior to any `git commit`.
   - Prevent commits containing PEP 8 violations, trailing whitespace, unformatted files, or high-severity security vulnerabilities from ever entering local git history.

2. **Continuous Integration (CI) Pipelines (e.g., GitHub Actions, GitLab CI):**
   - Automatically trigger automated static checks on every Pull Request (PR) and push to main branches.
   - Enforce quality gates:
     - **Bandit:** Fail CI builds if any High or Medium severity vulnerability is detected.
     - **Pylint:** Enforce a minimum score threshold (e.g., `>= 9.5/10.0`), failing builds if regressions drop the score.
     - **Flake8:** Zero-tolerance policy for style and syntax warnings.

3. **Shared Repository Configuration Files:**
   - Check configuration files into the root of the repository (`.pylintrc`, `.flake8` or `setup.cfg`, `bandit.yaml`).
   - Ensures consistent enforcement across diverse developer workstations and CI runners.
   - Require written documentation and code-review approval for any `# nosec` or `# pylint: disable` annotations.

---

## 4. What tangible improvements did you see in the code?

The improvements achieved across the codebase were substantial:

- **Security Hardening:**
  - **Eliminated Command Injection (CWE-78):** Replaced insecure `os.system` string concatenation with parameterized, shell-less `subprocess.run`, strict hostname regex validation, and `--` flag isolation.
  - **Cryptographic Integrity (CWE-327):** Replaced obsolete, collision-prone MD5 hashing with SHA-256.
  - **Credential Security (CWE-259):** Removed committed hardcoded secrets, replacing them with environment variable lookups.
  - **Unpredictable Randomness (CWE-330):** Upgraded bonus question selection to cryptographically secure `secrets.choice`.

- **Bug Resolution and Defect Elimination:**
  - **Fixed Mutable Default Argument (`W0102`):** Corrected `penalties={}` to `penalties=None`, preventing cross-call state leakage between student grading operations.
  - **Handled Empty Collections in `topper()`:** Added guards to prevent uncaught `ValueError` when grading tables are unpopulated.
  - **Isolated Module Imports:** Guarded execution behind `if __name__ == "__main__":`, allowing the module to be imported and unit-tested without side effects.

- **Maintainability, Readability, and Style:**
  - **Pylint Score Improvement:** Raised the code rating from **5.65/10** to a perfect **10.00/10**.
  - **Flake8 PEP 8 Compliance:** Reduced style violations from 4 to 0, ensuring consistent whitespace, spacing, and standard naming conventions (`snake_case`).
  - **Documentation:** Added clear PEP 257 docstrings for the module and all functions, establishing explicit API contracts and readability.
  - **Functional Integrity:** Validated that the program output, grading results, class average (2.0), and student rankings remained identical to original specification.
