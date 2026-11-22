# Scope

Write the scope down before every run. A run without a written scope is not
authorized.

## Template

- Target: <host / IP range / URL>
- Authorized by: <who, when, in what form>
- Allowed: <recon / scanning / exploitation / reporting>
- Forbidden: <production data, other tenants, destructive actions, ...>
- Time window: <start – end>

## Hard exclusions

- Your own machine, loopback (127.0.0.1), and the operator's infrastructure.
- The competition / event organizer's infrastructure, unless it is explicitly
  listed as a designated target.
- Anything outside the written scope, even if it looks vulnerable.

## Proof

Save the command, the output, and what changed. No proof = not done.
