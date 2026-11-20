# Release Server Executables

## Requirement: Build on the requested version conditions

The repository SHALL build a versioned deployable server executable when the
canonical version is exactly `2.0.1` or has a greater major component than
the previous release version.

### Scenario: The exact 2.0.1 version is pushed

- **GIVEN** the canonical version is `2.0.1`
- **WHEN** a commit containing that version is pushed
- **THEN** the workflow builds the server executable
- **AND** it publishes the versioned executable as a workflow artifact

### Scenario: The major version increases

- **GIVEN** the previous release is `2.0.0`
- **WHEN** version `3.0.0` is pushed
- **THEN** the workflow builds and publishes the versioned server executable

### Scenario: A non-triggering version is pushed

- **GIVEN** the previous release is `2.0.0`
- **WHEN** version `2.0.1` is not the current version and the current version
  has no greater major component
- **THEN** the workflow does not publish a server executable
- **AND** it reports that the build condition was not met

## Requirement: Keep the server executable deployable

The published executable SHALL contain the backend, Python runtime,
dependencies, and complete frontend while preserving the `/app/` route. It
SHALL exclude private keys and mutable runtime data.

### Scenario: The executable is downloaded and run

- **GIVEN** a workflow build was triggered
- **WHEN** an operator runs the executable on its matching target platform
- **THEN** the HTTPS server starts without a Python installation
- **AND** the page and its referenced assets are available at `/app/`
- **AND** no private key or mutable runtime data is embedded in the
  executable

### Scenario: A target dependency is missing

- **GIVEN** the executable cannot find its required certificate or native
  Tesseract dependency
- **WHEN** the operator starts it
- **THEN** startup fails with an explicit error naming the missing dependency
