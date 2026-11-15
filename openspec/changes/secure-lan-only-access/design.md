# Design: Secure LAN-only access

## Access policy

The default policy permits loopback and private address ranges only:

- IPv4 loopback and RFC1918 ranges.
- IPv6 loopback and link-local/private ranges supported by the runtime.

All other client addresses receive an explicit forbidden response. The
application must inspect the connected client address, not an untrusted
forwarded header. Forwarded headers must not expand access unless a trusted
proxy configuration is introduced separately.

## Launcher behavior

The launcher should retain a usable LAN bind mode but make the access policy
explicit in its CLI help and startup output. A public-access override, if
needed for development, must be opt-in and clearly named rather than silently
enabled by a host default.

The default Windows firewall guidance should allow the HTTPS port only on the
Private profile. Documentation must state that router port forwarding and UPnP
can bypass local-network assumptions.

## Error behavior

Rejected clients receive HTTP 403 with a stable, non-sensitive message. The
server logs the rejection at an appropriate level without logging credentials
or private request data.

## Validation

Tests must cover loopback, representative private addresses, public addresses,
and forwarded-header spoofing. Existing health, API, frontend, and HTTPS
startup behavior must remain covered.
