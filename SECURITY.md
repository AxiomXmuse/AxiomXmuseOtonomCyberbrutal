# Security Policy

## Authorized use only

This repo is a red-team / security-testing harness. Use it only against targets
you are authorized to test: your own lab, a CTF / hackathon sandbox, or a
target with a written scope or bug-bounty program.

Do not use it against production systems, other people's infrastructure,
or for spam, harassment, or abuse. Abuse tools (SMS / OTP bombers and
similar) are not in this repo and must not be added.

## Reporting a vulnerability in this repo

If you find a real credential, a secret, or a vulnerability in this repo
itself, do not open a public issue with the details. Contact the repo owner
directly and rotate the credential first.

## Secret scanning

`gitleaks dir .` from the repo root must be clean before any push.
Verified example tokens in skill documentation are listed in
`.gitleaksignore` by fingerprint. No real credential is ignored, and new
secrets are still flagged.
