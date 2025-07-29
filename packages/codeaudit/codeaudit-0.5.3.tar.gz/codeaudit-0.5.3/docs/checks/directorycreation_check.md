# Directory Creation

Creation of a directory from within a Python program can pose security issues if not handled carefully. 


**1. Directory Traversal/Path Manipulation:**

* **Risk:** If your program takes user-provided input for directory names or paths and directly uses it to create directories without proper sanitization, an attacker could supply paths like `../../../../etc/malicious_dir` to create directories outside of the intended scope. This could lead to:
    * **Overwriting or interfering with system files/directories:** An attacker might create a directory with the same name as a critical system file, potentially causing the system to malfunction or execute malicious code.
    * **Denial of Service (DoS):** Creating directories in critical system locations or filling up disk space in unexpected places.
    * **Information Disclosure:** If the attacker can control the path where other files are written, they might be able to read or write to sensitive locations.
* **Mitigation:**
    * **Validate and Sanitize Input:** Never trust user input. Always sanitize paths by:
        * **Restricting to a Base Directory:** Use `os.path.abspath()` and `os.path.join()` to construct absolute paths and then check that the resulting path is a sub-path of an allowed base directory.
        * **Normalizing Paths:** Use `os.path.normpath()` to resolve `.` and `..` components in paths, making it easier to check for traversal attempts.
        * **Filtering Invalid Characters:** Remove or replace characters that are not allowed in directory names on the target operating system (e.g., `/`, `\`, `*`, `?`, etc.).
    * **Use `pathlib` module:** The `pathlib` module (introduced in Python 3.4) offers a more object-oriented and safer way to handle paths. It can help you construct paths more robustly and handle exceptions.

**2. Permission Issues:**

* **Risk:**
    * **Overly Permissive Directories:** If you create directories with overly permissive modes (e.g., `0o777` or `777` which means read, write, and execute for everyone), it can allow other users or processes on the system to read, write, or delete files within that directory. This could lead to:
        * **Data Tampering:** Malicious users could modify or delete important data.
        * **Code Injection:** If your program later executes files from this directory, an attacker could inject malicious code.
    * **Insufficient Permissions:** If your program runs with limited permissions and tries to create a directory in a protected location, it will fail, potentially causing a DoS for your application.
* **Mitigation:**
    * **Set Appropriate Permissions (`mode` argument):** When using `os.mkdir()` or `os.makedirs()`, always specify the `mode` argument to set appropriate permissions. For example, `mode=0o755` is a common choice, granting the owner full permissions and others read and execute access, but not write access.
    * **Understand `umask`:** On Unix-like systems, the `umask` affects the actual permissions of newly created files and directories. Python's `os.mkdir` and `os.makedirs` respect the `umask`. Be aware of the `umask` of the process running your Python script.
    * **Principle of Least Privilege:** Your Python program (or the user account it runs under) should only have the minimum necessary permissions to perform its tasks. Avoid running the script as root or with elevated privileges if not absolutely essential.

**3. Race Conditions:**

* **Risk:** When you check if a directory exists (`os.path.exists()`) and then try to create it (`os.makedirs()`), there's a small window of time (a "race condition") where another process or thread could create the directory, or even a file with the same name, before your `makedirs` call. This can lead to `FileExistsError` or `IsADirectoryError`, or worse, your program interacting with an unintended file.
* **Mitigation:**
    * **Use `exist_ok=True`:** The `os.makedirs()` function (and `pathlib.Path.mkdir()`) has an `exist_ok=True` argument (available in Python 3.2+). This tells the function to not raise an error if the target directory already exists. This is generally the safest way to create directories if you don't need to specifically handle the "already exists" case.
    * **Robust Error Handling:** Even with `exist_ok=True`, it's good practice to wrap directory creation in `try-except` blocks to catch `PermissionError` or other `OSError` exceptions that might occur due to insufficient disk space, invalid path segments, etc.

**4. Temporary Directory Creation (and `mktemp()`):**

* **Risk:** Historically, `os.mktemp()` was vulnerable because it generated predictable temporary filenames, creating a race condition where a malicious actor could create a file with that name before your program did. This could lead to your program operating on a malicious file.
* **Mitigation:**
    * **Use `tempfile` module:** Python's `tempfile` module is specifically designed for secure creation of temporary files and directories. Use functions like `tempfile.mkdtemp()` to create unique and secure temporary directories. These functions handle race conditions and permissions correctly. **Never use `os.mktemp()` in new code.**

**Best Practices for Secure Directory Creation:**

1.  **Validate All Input:** Especially if coming from external sources (users, network, configuration files).
2.  **Use `os.makedirs(path, mode, exist_ok=True)` or `pathlib.Path(path).mkdir(parents=True, exist_ok=True)`:** These are the preferred and safest ways to create directories, handling recursive creation and avoiding errors if the directory already exists.
3.  **Set Appropriate Permissions (`mode`):** Be explicit about directory permissions. Avoid `0o777`.
4.  **Use `tempfile` for Temporary Directories:** Leverage `tempfile.mkdtemp()` for secure temporary directory creation.
5.  **Principle of Least Privilege:** Run your Python program with the minimum necessary permissions on the operating system.
6.  **Error Handling:** Implement `try-except` blocks to gracefully handle potential `OSError` exceptions (e.g., `PermissionError`, `FileExistsError`, `FileNotFoundError`).

By following these guidelines, you can significantly reduce the security risks associated with creating directories from within your Python programs.

## More information

* https://docs.python.org/3/library/os.html

