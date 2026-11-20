# Delta for Runtime Operation

## MODIFIED Requirements

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
