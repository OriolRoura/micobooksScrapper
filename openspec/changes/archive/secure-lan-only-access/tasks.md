# Tasks

## 1. Network access policy

- [x] 1.1 Add a typed helper for determining whether a client address is allowed
- [x] 1.2 Reject non-local and non-private clients with HTTP 403
- [x] 1.3 Ignore untrusted forwarded headers when enforcing the policy
- [x] 1.4 Add focused tests for IPv4/IPv6 loopback, private, public, and spoofed-header cases

## 2. Launcher and configuration

- [x] 2.1 Preserve LAN usability while making the LAN-only policy the default
- [x] 2.2 Add an explicit, clearly named opt-in for public access if required
- [x] 2.3 Update launcher help and startup messages to describe the active access policy
- [x] 2.4 Add tests for default and explicit launcher policy behavior

## 3. Documentation and operational guidance

- [x] 3.1 Update README startup and firewall instructions for LAN-only access
- [x] 3.2 Document that HTTPS encrypts traffic but is not an access-control mechanism
- [x] 3.3 Warn against router port forwarding and UPnP for this service
- [x] 3.4 Update the runtime-operation specification after implementation

## 4. Verification

- [x] 4.1 Run the focused security and launcher tests
- [x] 4.2 Run the complete unittest suite
- [x] 4.3 Start the HTTPS server locally and verify the health endpoint
