# Publication checker note

After PUBLICATION-INTEGRITY.json was written, a final receipt/whitespace checker
confirmed hashes but failed reading Markdown using Windows' default cp1252 encoding
(`UnicodeDecodeError`). The checker was repeated with explicit UTF-8 and passed
all receipt hashes and new-artifact trailing-whitespace checks. No artifact, FRC,
first result or implementation was changed in response. This is a publication
checker correction, not a requirement evaluation rerun or software remediation.
