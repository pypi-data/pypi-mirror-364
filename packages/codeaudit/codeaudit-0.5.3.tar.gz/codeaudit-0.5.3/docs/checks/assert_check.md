# Assert Statement

The Python `assert` statement itself is not inherently insecure, but its *misuse* can lead to security vulnerabilities. The key lies in understanding its intended purpose and limitations.

Using `assert` can be problematic from a security perspective:

1. Assertions are primarily for debugging and development, NOT for production validation or error handling.

* **They can be disabled:** When Python is run in optimized mode (with the `-O` or `-OO` flags, or by setting the `PYTHONOPTIMIZE` environment variable), `assert` statements are completely ignored. This means any crucial checks you rely on for security or data integrity will simply vanish, leaving your application vulnerable.
* **Not for user input validation:** Never use `assert` to validate user input or external data. If assertions are disabled in production, malicious or malformed input will bypass your checks, potentially leading to crashes, data corruption, or even arbitrary code execution. Use `if/else` statements with proper exception handling (e.g., `ValueError`, `TypeError`) for this.
* **Not for graceful error handling:** Assertions are designed to signal "this should never happen, it's a bug." They raise an `AssertionError` which typically halts the program. In a production environment, you usually want to handle anticipated errors gracefully, log them, and potentially recover or inform the user, rather than crashing the application.

2. Side effects within `assert` statements can be dangerous.**

* If an `assert` statement contains code with side effects (e.g., modifying a variable, calling a function that performs an action), those side effects will also be skipped when assertions are disabled. This can lead to unexpected behavior and security gaps.


`assert` is a valuable Python default statement when used correctly:

* **Debugging:** Catching bugs early in development by verifying assumptions about your code's internal state.
* **Testing:** Used extensively in unit tests (e.g., with `pytest`) to verify the correctness of functions and methods.
* **Documenting invariants:** Highlighting conditions that should always be true at a certain point in your code, acting as "executable documentation."
* **Preconditions and postconditions (internal):** Ensuring that certain conditions hold before or after a function executes, where a failure indicates a bug in your own code, not invalid external input.

`Assert` helps to find mistakes during development. But it is not a security fence to protect against external threats or a robust mechanism for handling runtime issues in a live system. For production code, especially when dealing with external inputs or critical business logic, rely on explicit `if/else` checks and robust exception handling.

 `Assert` statements should in general only be used for debugging purposes. They are removed when not running in debug mode (i.e. when invoking the Python command with the -O or -OO options).

## How to solve
Use a raise statement to throw a proper, informative runtime exception, if you need to. 
That would definitely be best practice when there'd otherwise be no sensible return value for the function. 

In general `assert` is good to use for `pytest` or other development constructs. But use for production code is not recommended. However using is not direct a security issue or potential vulernability. That's why this `codeaudit` tool reports **potential** issues [DOC](tbd).


## More information

* [The assert statement - Python Documentation](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)
* [The dangers of assert in Python](https://snyk.io/blog/the-dangers-of-assert-in-python/)
* [Feature: Python assert should be consider harmful](https://community.sonarsource.com/t/feature-python-assert-should-be-consider-harmful/38501) But note that Sonar did not implement this check.