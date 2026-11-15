# Web Interface

The application serves a mobile-first frontend from the FastAPI server.

### Requirement: Provide the analysis interface

The frontend SHALL allow users to submit an ISBN manually or upload/capture a
book image, then display the returned quotation or an actionable error.

#### Scenario: A user performs a manual lookup

- **GIVEN** the frontend is loaded
- **WHEN** the user submits an ISBN
- **THEN** the frontend sends the ISBN to the quotation API
- **AND** it displays the returned book and seller estimate

#### Scenario: A manual lookup fails

- **GIVEN** the quotation API rejects or cannot complete the lookup
- **WHEN** the frontend receives the response
- **THEN** it displays the returned error to the user
- **AND** it does not display a stale quotation as the new result

#### Scenario: A user performs an image lookup

- **GIVEN** the user selects or captures an image
- **WHEN** the image is submitted
- **THEN** the frontend sends it to the image quotation API
- **AND** it displays the returned quotation or the API error

### Requirement: Manage history from the interface

The frontend SHALL display stored history and allow users to refresh, import,
download, and update sell decisions.

#### Scenario: The history drawer is opened

- **WHEN** the user opens history
- **THEN** the frontend loads and displays records from the history API
- **AND** it shows the count and total profit for records marked sell

#### Scenario: A user captures a camera image

- **GIVEN** the page is loaded in a browser with camera access
- **WHEN** the user starts the camera and takes a photo
- **THEN** the captured image becomes available for submission
- **AND** the camera stream is stopped after capture

#### Scenario: Camera access is unavailable

- **GIVEN** the browser does not support camera access or permission is denied
- **WHEN** the user starts the camera
- **THEN** the interface displays an actionable error
- **AND** the user can choose an image file instead

#### Scenario: A user imports history

- **GIVEN** the user selects a JSON file containing history records with ISBN values
- **WHEN** the file is read successfully
- **THEN** the frontend displays the imported records locally
- **AND** it does not overwrite server history

#### Scenario: A user exports history

- **WHEN** the user chooses to download history
- **THEN** the frontend downloads the currently displayed records as JSON

#### Scenario: A user changes a sell decision

- **GIVEN** a displayed found record
- **WHEN** the user selects Sell or Do not sell
- **THEN** the decision is saved to the server for server history
- **OR** updated locally for imported history
- **AND** the summary and marked-sell total are recalculated

### Requirement: Serve the frontend

The application SHALL serve the frontend from the API application under the
`/app/` path.

#### Scenario: The frontend is requested

- **WHEN** a user opens the frontend path
- **THEN** the application serves the web interface

### Requirement: Report service status

The API SHALL expose a discovery response and a health endpoint.

#### Scenario: The root endpoint is requested

- **WHEN** a client requests `/`
- **THEN** the API identifies the application and links to health, docs,
  frontend, and quotation functionality

#### Scenario: The health endpoint is requested

- **WHEN** a client requests `/health`
- **THEN** the API returns an `ok` status
