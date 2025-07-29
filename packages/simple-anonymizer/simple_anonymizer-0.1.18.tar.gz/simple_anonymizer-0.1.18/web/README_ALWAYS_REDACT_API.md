# Always-Redact Web API Documentation

The web application now includes full API support for managing always-redact words. These endpoints allow you to add, remove, and list words that should always be redacted regardless of context.

## Important Features

- ✅ **Real-time file refresh**: Changes are picked up immediately without restarting the app
- ✅ **Thread-safe**: Multiple requests can safely modify the always_redact list
- ✅ **Persistent**: Changes are saved to `~/.anonymizer/always_redact.txt`
- ✅ **Compatible**: Works seamlessly with CLI and GUI management

## API Endpoints

### 1. List Always-Redact Words

**GET** `/api/v1/always-redact`

Returns all words currently in the always-redact list.

```bash
curl -X GET http://localhost:5000/api/v1/always-redact
```

**Response:**
```json
{
  "words": ["confidential", "secret", "private"],
  "count": 3
}
```

### 2. Add Word to Always-Redact List

**POST** `/api/v1/always-redact/add`

Adds a word to the always-redact list.

```bash
curl -X POST http://localhost:5000/api/v1/always-redact/add \
  -H "Content-Type: application/json" \
  -d '{"word": "confidential"}'
```

**Response (success - new word):**
```json
{
  "message": "Successfully added \"confidential\" to always-redact list",
  "word": "confidential",
  "action": "added"
}
```

**Response (word already exists):**
```json
{
  "message": "\"confidential\" is already in the always-redact list",
  "word": "confidential", 
  "action": "already_exists"
}
```

### 3. Remove Word from Always-Redact List

**POST** `/api/v1/always-redact/remove`

Removes a word from the always-redact list.

```bash
curl -X POST http://localhost:5000/api/v1/always-redact/remove \
  -H "Content-Type: application/json" \
  -d '{"word": "confidential"}'
```

**Response (success):**
```json
{
  "message": "Successfully removed \"confidential\" from always-redact list",
  "word": "confidential",
  "action": "removed"
}
```

**Response (word not found):**
```json
{
  "message": "\"confidential\" not found in always-redact list",
  "word": "confidential",
  "action": "not_found"
}
```

## Integration with Anonymization

Words in the always-redact list are automatically applied during anonymization:

```bash
# Add a word
curl -X POST http://localhost:5000/api/v1/always-redact/add \
  -H "Content-Type: application/json" \
  -d '{"word": "confidential"}'

# Anonymize text - "confidential" will be redacted
curl -X POST http://localhost:5000/api/v1/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text": "This confidential document contains secrets."}'
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input (empty word, malformed JSON, etc.)
- `415 Unsupported Media Type`: Missing or incorrect Content-Type header
- `500 Internal Server Error`: Server-side error

**Example error response:**
```json
{
  "error": "Word cannot be empty"
}
```

## Real-Time Updates

The always-redact system reads from the file on every anonymization request, so:

1. ✅ **Web API changes** are immediately available to CLI/GUI
2. ✅ **CLI changes** are immediately available to Web API
3. ✅ **GUI changes** are immediately available to Web API
4. ✅ **Direct file edits** are immediately picked up by all interfaces

## File Location

Always-redact words are stored in: `~/.anonymizer/always_redact.txt`

The file is automatically created if it doesn't exist, and changes via any interface (Web API, CLI, GUI, or direct editing) are immediately available to all other interfaces.

## Security Notes

- Words are validated for length (max 100 characters)
- Only alphanumeric characters and common punctuation should be used
- The always-redact list overrides protected titles when explicitly configured
- File permissions are managed securely by the system