# ISBN Quoting

The application identifies a book from a manually entered ISBN/EAN or from
an uploaded image, then returns the seller estimate available from Micobooks.

### Requirement: Manual ISBN quotation

The API SHALL accept an ISBN or EAN containing 10 to 13 valid characters and
return the matching book title, identifiers, seller profit, and optional cover
image URL.

#### Scenario: A quotation is found

- **GIVEN** a user submits a valid ISBN or EAN
- **WHEN** the remote Micobooks service returns a matching item
- **THEN** the API returns the item's title, identifiers, seller profit, and image URL
- **AND** the analysis is recorded in local history as found

#### Scenario: The identifier is invalid

- **GIVEN** a user submits an identifier containing invalid characters or length
- **WHEN** the API validates the request
- **THEN** it returns a client error explaining the accepted ISBN/EAN format
- **AND** it records the analysis as not found

#### Scenario: Micobooks is unavailable

- **GIVEN** a syntactically valid identifier
- **WHEN** the remote service fails or returns malformed data
- **THEN** the API returns an upstream-service error
- **AND** the analysis is recorded as not found

### Requirement: Image upload quotation

The API SHALL accept image uploads up to 10 MB and return a quotation for the
first detected identifier with a matching Micobooks result.

#### Scenario: A non-image upload is submitted

- **GIVEN** an uploaded file whose content type is not an image
- **WHEN** the API validates the upload
- **THEN** it rejects the request with an unsupported-media-type error

#### Scenario: An oversized image is submitted

- **GIVEN** an image larger than 10 MB
- **WHEN** the API validates the upload
- **THEN** it rejects the request with a payload-too-large error

### Requirement: Image ISBN detection

The application SHALL try barcode decoding before using OCR to find unique,
checksum-valid ISBN-10 or ISBN-13 candidates.

#### Scenario: An ISBN is detected and quoted

- **GIVEN** the user uploads an image containing a valid ISBN barcode or printed ISBN
- **WHEN** barcode decoding or OCR detects candidates and Micobooks has a quotation
- **THEN** the API returns the quotation using the detected identifier
- **AND** the analysis is recorded in local history

#### Scenario: No usable ISBN is detected

- **GIVEN** the user uploads an image without a valid ISBN
- **WHEN** barcode decoding and OCR complete
- **THEN** the API returns an error stating that no valid ISBN was detected

#### Scenario: A detected identifier has no quotation

- **GIVEN** image analysis detects one or more valid identifiers
- **WHEN** Micobooks has no quotation for any candidate
- **THEN** the API returns a not-found error listing the searched identifiers
- **AND** each unsuccessful candidate is recorded as not found

#### Scenario: OCR is unavailable

- **GIVEN** the image requires OCR and the OCR engine is unavailable
- **WHEN** image analysis runs
- **THEN** the API returns a service-unavailable error explaining the dependency
