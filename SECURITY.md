# Security and scope

This project **does not sandbox code**. Every candidate module is imported and executed
with the privileges of the Python process. The timeout only limits how long the direct
worker process is awaited. It is not protection against malicious subprocesses, filesystem
access, network access, or deliberate evasion.

Run only examples you created or whose source you have reviewed and trust. Never point
this tool at unknown code from the internet or confidential employer assessment files.
Use disposable, properly isolated infrastructure for evaluating adversarial submissions.
No external model API, credentials, or employer-specific materials are included.
