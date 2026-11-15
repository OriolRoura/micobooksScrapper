# Analysis History

The application stores analyzed book results in a local JSON file and exposes
history operations to the frontend.

### Requirement: Persist analyzed books

The application SHALL persist each analyzed ISBN with its timestamp, title,
seller profit, found state, and sell decision.

#### Scenario: A new ISBN is analyzed

- **GIVEN** an ISBN has not previously been recorded
- **WHEN** its analysis completes
- **THEN** a record is written to the local JSON history file
- **AND** the record receives a unique identifier and an ISO timestamp

#### Scenario: Equivalent ISBN forms are analyzed

- **GIVEN** an ISBN-10 and its equivalent 978 ISBN-13 are analyzed
- **WHEN** the history is updated
- **THEN** the equivalent identifiers are deduplicated into one record

#### Scenario: A failed analysis is retried successfully

- **GIVEN** an identifier already exists as not found
- **WHEN** a later analysis finds a quotation
- **THEN** the existing record is updated with the successful result
- **AND** no duplicate record is created

#### Scenario: The history file is missing or invalid

- **GIVEN** the history file does not exist or contains invalid JSON
- **WHEN** the store is initialized or read
- **THEN** the application treats history as empty
- **AND** subsequent writes restore a valid JSON history file

### Requirement: Read history newest first

The API SHALL return stored history records in reverse chronological order.

#### Scenario: History is requested

- **WHEN** a client requests the history endpoint
- **THEN** the response contains the newest analyzed records first

#### Scenario: History is empty

- **WHEN** a client requests history before any analysis exists
- **THEN** the API returns an empty array

### Requirement: Set a sell decision

The API SHALL allow a history record to be marked `sell` or `not_sell`.

#### Scenario: A valid decision is submitted

- **GIVEN** the requested history record exists
- **WHEN** the client submits a supported decision
- **THEN** the record is updated and returned

#### Scenario: An unsupported decision is submitted

- **GIVEN** a client submits a decision other than `sell` or `not_sell`
- **WHEN** the API validates the request
- **THEN** it rejects the request as invalid

#### Scenario: The record does not exist

- **GIVEN** the requested history record does not exist
- **WHEN** the client submits a decision
- **THEN** the API returns a not-found error
