# Pickle

Unpickling will import any class or function that it finds in the pickle data. This is a severe security concern as it permits the unpickler to import and invoke arbitrary code. 

The primary security concern with the `pickle` module in Python revolves around **deserialization of untrusted data**.

Specifically, the main call that poses a security risk is:

* **`pickle.load()`** (and its variations like `pickle.loads()` for bytes)

**Why `pickle.load()` is dangerous with untrusted data:**

When you use `pickle.load()` to deserialize a byte stream, the `pickle` module essentially reconstructs Python objects from that stream. A malicious attacker can craft a pickled payload that, when deserialized, can:

1.  **Execute arbitrary code:** The `pickle` protocol can be manipulated to cause the deserializer to import arbitrary modules and call arbitrary functions with arbitrary arguments. This means an attacker can execute system commands, delete files, or do anything else the Python process running `pickle.load()` has permissions to do. This is often referred to as a "deserialization vulnerability" or "arbitrary code execution."
2.  **Cause Denial of Service (DoS):** An attacker could create a pickled object that, when deserialized, consumes excessive memory or CPU resources, leading to your application crashing or becoming unresponsive.


**Never use `pickle.load()` or `pickle.loads()` on data received from an untrusted or unauthenticated source.**

If you need to serialize data for storage or transmission, and the data might come from or be exposed to untrusted parties, consider safer alternatives like:

* **JSON:** For simple data structures (dictionaries, lists, strings, numbers, booleans). It's human-readable and doesn't execute code on deserialization.
* **YAML:** Similar to JSON but often more human-friendly for configuration files.
* **Protocol Buffers, Avro, Thrift:** For more complex, schema-defined data, especially in distributed systems. They offer strong typing and efficient serialization.


## More information

* https://docs.python.org/3/library/pickle.html#pickle-restrict