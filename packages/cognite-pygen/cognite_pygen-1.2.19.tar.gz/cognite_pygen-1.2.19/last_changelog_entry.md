
### Fixed

- Calling `.upsert()` on an instance that has a direct relations without
a source specified and with that direct relation as a string
(externalId) no longer raises a `CogniteAPIError`.