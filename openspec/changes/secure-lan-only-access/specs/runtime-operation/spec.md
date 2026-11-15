# Delta for Runtime Operation

## MODIFIED Requirements

### Requirement: Start the HTTPS service

The launcher SHALL start the application with configurable host, port,
certificate, and private-key paths while enforcing LAN-only client access by
default.

#### Scenario: The default launcher is started

- **GIVEN** the default certificate and private key exist
- **WHEN** the launcher is started without arguments
- **THEN** it serves HTTPS on the default port and bind address
- **AND** it permits localhost and private-LAN clients only

#### Scenario: A public-access override is explicitly selected

- **GIVEN** a developer intentionally selects the documented public-access override
- **WHEN** the launcher is started
- **THEN** it clearly reports that public access is enabled
- **AND** the default LAN-only policy is not silently disabled

#### Scenario: TLS files are missing

- **GIVEN** one or more configured TLS files do not exist
- **WHEN** the launcher is started
- **THEN** it stops with an explicit error naming the missing files

### Requirement: Support local-network access

The service SHALL allow localhost and private LAN clients while rejecting
public client addresses unless an explicit public-access override is enabled.

#### Scenario: A private-LAN client connects

- **GIVEN** the HTTPS port is reachable and the client uses a private address
- **WHEN** the client requests the API or frontend
- **THEN** the request is served normally

#### Scenario: A public client connects

- **GIVEN** the LAN-only policy is active
- **WHEN** a client with a public address requests the service
- **THEN** the service returns HTTP 403
- **AND** it does not rely on an untrusted forwarded header to grant access

#### Scenario: The Windows firewall is configured

- **GIVEN** the HTTPS port is allowed through Windows Firewall
- **WHEN** the rule is scoped to the Private network profile
- **THEN** local-network clients can connect without making the service an
  intended public endpoint
