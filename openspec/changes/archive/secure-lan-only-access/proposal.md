# Proposal: Secure LAN-only access

## Intent

Restrict the Micobooks service to local-machine and private-LAN clients by
default while keeping the application usable without accounts.

## Current state

The HTTPS launcher in `micobooks_scraper/server.py` binds to `0.0.0.0` by
default. The application has no network-level client restriction, so a public
interface or router port-forward could expose the API.

## Target state

The service SHALL accept requests from localhost and private LAN addresses by
default, reject public client addresses, and make any public exposure an
explicit opt-in. HTTPS remains required for the normal launcher.

## Scope

- Add LAN-only request filtering that does not require user accounts.
- Preserve local browser and local-network device access.
- Make public binding or public access explicit and visible.
- Update launcher help, README instructions, and focused tests.
- Keep certificate and private-key handling unchanged except for related
  security guidance.

## Impact

This is a security-hardening change. Clients outside localhost or private
address ranges will no longer be able to use the service by default. Existing
LAN clients should continue to work when the Windows firewall permits the
configured HTTPS port.

## Out of scope

- User accounts, passwords, sessions, or token authentication.
- Internet-facing deployment.
- Replacing the existing HTTPS certificate workflow.
