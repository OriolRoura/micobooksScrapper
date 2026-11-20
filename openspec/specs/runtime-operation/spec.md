# Runtime Operation

The application provides a local HTTPS launcher for serving the API and
frontend to the local machine or another device on the same network.

### Requirement: Start the HTTPS service

The launcher SHALL start the application with configurable host, port,
certificate, and private-key paths while enforcing LAN-only client access by
default.

#### Scenario: The default launcher is started

- **GIVEN** the default certificate and private key exist
- **WHEN** the launcher is started without arguments
- **THEN** it serves HTTPS on the default port and bind address
- **AND** it permits localhost and private-LAN clients only

#### Scenario: Custom server settings are provided

- **GIVEN** valid host, port, certificate, and private-key arguments
- **WHEN** the launcher is started
- **THEN** it serves HTTPS using those settings

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

### Requirement: Support Raspberry Pi 4 Linux deployment

The project SHALL provide a documented Raspberry Pi 4 Linux deployment path
for the HTTPS application without changing the existing API, persistence, or
LAN-only security defaults.

#### Scenario: Raspberry Pi dependencies are installed

- **GIVEN** a supported 64-bit Raspberry Pi OS installation
- **WHEN** an operator follows the documented setup
- **THEN** Python dependencies and native Tesseract prerequisites can be
  installed using supported Linux tooling
- **AND** the HTTPS launcher can be started from the project virtual
  environment

#### Scenario: A Raspberry Pi service is started

- **GIVEN** valid certificate and private-key files are present
- **WHEN** the operator starts the documented Linux service or launcher
- **THEN** the application serves HTTPS on the configured LAN address and
  port
- **AND** LAN-only client filtering remains enabled by default

#### Scenario: OCR runs under the Pi resource profile

- **GIVEN** the Raspberry Pi resource profile is enabled
- **WHEN** an image is submitted for ISBN extraction
- **THEN** preprocessing and OCR use the configured image and worker limits
- **AND** the request does not create more OCR workers than configured

#### Scenario: Existing API behavior is preserved

- **GIVEN** a valid ISBN image or manual ISBN request
- **WHEN** the request is processed on Raspberry Pi Linux
- **THEN** the response uses the existing API schema and status behavior
- **AND** successful analysis is stored using the existing local history format
