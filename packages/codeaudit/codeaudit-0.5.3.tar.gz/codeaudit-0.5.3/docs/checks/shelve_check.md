# Shelve


Because the shelve module is backed by pickle, it is insecure to load a shelf from an untrusted source. Like with pickle, loading a shelf can execute arbitrary code.

The Python shelve module provides a persistent, dictionary-like object. It allows you to store Python objects directly to a file, and retrieve them later, making it seem very convenient for simple data persistence. However, shelve is not secure for handling data from untrusted sources due to its underlying mechanism: it uses the pickle module for serialization and deserialization.

Security concerns:

1. Reliance on pickle
The shelve module essentially wraps the pickle module. When you store an object in a shelve database, it's pickled (serialized) and written to a file. When you retrieve an object, it's unpickled (deserialized) from the file.

2. The pickle Security Vulnerability
The core of the security issue lies with pickle. The pickle module is powerful because it can serialize and deserialize almost any Python object, including instances of classes, functions, and even code objects. To achieve this, pickle's deserialization process is designed to reconstruct Python objects by executing a sequence of bytecode instructions.

The critical vulnerability is this: If a malicious actor can provide you with a specially crafted pickled payload (or modify an existing shelve file), when your application attempts to unpickle this data, it can execute arbitrary code on your system. This is often referred to as a "deserialization vulnerability."


3. How This Affects shelve
Because shelve uses pickle, it inherits this exact same vulnerability. If an attacker can:

Supply a malicious shelve file: If your application opens a shelve database created or modified by an untrusted party, attempting to read from it could lead to arbitrary code execution.

Inject malicious data into an existing shelve: If an attacker can write to or modify the shelve file directly, they can insert malicious pickled objects that will execute when your application next reads from the shelve.

4. Scenarios Where It's Insecure
Web Applications: If a web application uses shelve to store user-submitted data, and that data is later loaded, a malicious user could exploit this to execute code on the server.

Shared File Systems: If a shelve file is stored on a shared network drive or a system where untrusted users have write access, they could tamper with the file.

Client-Side Data (less common for shelve): While shelve is typically server-side, any scenario where you load shelve data from an untrusted client is dangerous.

5. Secure Alternatives
For persistent storage, especially when dealing with untrusted data or when security is a concern, consider these alternatives:

JSON (JavaScript Object Notation): For simple data structures (dictionaries, lists, strings, numbers, booleans, null). JSON is a data format, not a code execution mechanism, making it much safer.

YAML: Similar to JSON, but often considered more human-readable.

Databases (SQL or NoSQL):

SQLite: For simple, file-based relational databases.

PostgreSQL, MySQL, MongoDB, etc.: For more robust, scalable, and secure data storage. These systems have their own security models and query languages that prevent arbitrary code execution during data retrieval.

Protocol Buffers (Protobuf) or Apache Avro: For structured data serialization, often used in distributed systems, offering schema enforcement and efficiency.

Custom Serialization: If you absolutely need to store complex Python objects and have security concerns, implement your own serialization logic that explicitly handles only the data you expect, avoiding generic code execution.

In summary, while shelve is convenient for simple, trusted data persistence (e.g., local configuration files for a single-user application where the user is the only one interacting with the file), it should never be used with data that originates from or can be manipulated by untrusted sources.

## More information

* https://docs.python.org/3/library/shelve.html#shelve-security