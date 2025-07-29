# Teams Bot Utils

A comprehensive Python library for Microsoft Teams bot development, providing utilities for message processing, image handling, telemetry tracking, and HTTP client management with connection pooling.

## 🚀 Features

- **Message Analysis**: Analyze Teams messages for text, images, and file attachments
- **Image Processing**: Download and encode images from Teams attachments 
- **Telemetry Integration**: Track bot usage and user interactions with Mixpanel
- **HTTP Client Management**: Efficient connection pooling for external API calls
- **Activity Extensions**: Enhanced functionality for Bot Framework activities
- **Async Support**: Full async/await support for optimal performance

## 📦 Installation

```bash
pip install teams-bot-utils
```

## 🔧 Requirements

- Python 3.8+
- botbuilder-core>=4.14.0
- httpx>=0.24.0
- mixpanel>=2.2.0
- pydantic>=1.8.0

## 🎯 Quick Start

### Message Content Analysis

```python
from teams_bot_utils.extensions import extend_activity_class
from botbuilder.schema import Activity

# Extend the Activity class with helper methods
extend_activity_class()

# Analyze message contents
activity = Activity(text="Hello world", attachments=[...])
has_text, file_count, image_count, extensions = activity.check_message_contents()

print(f"Has text: {has_text}")
print(f"Files: {file_count}, Images: {image_count}")
print(f"File extensions: {extensions}")
```

### Image Processing

```python
from teams_bot_utils.images.processing import process_image_attachment, extract_image_from_activity

# Process a single image attachment
base64_image = await process_image_attachment(attachment)

# Extract first image from activity
image_data = await extract_image_from_activity(activity.attachments)
if image_data:
    print(f"Found image: {len(image_data)} bytes")
```

### Telemetry Tracking

```python
from teams_bot_utils.telemetry.mixpanel_telemetry import BotTelemetry

# Initialize telemetry
telemetry = BotTelemetry(token="your_mixpanel_token")

# Track user interactions
telemetry.track_message_received(
    user_id="user123",
    session_id="session456", 
    has_text=True,
    has_image=False,
    text_length=50
)

telemetry.track_response_sent(
    user_id="user123",
    session_id="session456",
    response_time_ms=250,
    success=True
)

# Advanced tracking with activity context
telemetry.identify_and_track(
    event="Custom Event",
    activity=teams_activity,
    properties={"custom_property": "value"}
)
```

### HTTP Client with Connection Pooling

```python
from teams_bot_utils.utils.http_client import HttpClient

# Create HTTP client with connection pooling
client = HttpClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=30.0
)

# Make requests
response = await client.get("/endpoint", params={"key": "value"})
data = await client.post("/submit", json_data={"data": "value"})

# Clean up (optional - clients auto-manage connections)
from teams_bot_utils.utils.http_client import close_all_clients
await close_all_clients()
```

## 📚 Detailed Usage

### Message Content Analysis

The library extends the Bot Framework's `Activity` class with enhanced message analysis:

```python
from teams_bot_utils.extensions import extend_activity_class

# Call once at startup
extend_activity_class()

async def on_message_activity(self, turn_context):
    activity = turn_context.activity
    
    # Analyze message contents
    has_text, file_count, image_count, extensions = activity.check_message_contents()
    
    if has_text:
        print(f"Message: {activity.text}")
    
    if image_count > 0:
        print(f"Found {image_count} images")
        # Process images
        image_data = await extract_image_from_activity(activity.attachments)
    
    if file_count > 0:
        print(f"Found {file_count} files with extensions: {extensions}")
```

### Advanced Image Processing

Handle various Teams attachment types:

```python
from teams_bot_utils.images.processing import (
    process_image_attachment,
    download_and_encode_image,
    extract_image_from_activity
)

# Process specific attachment types
for attachment in activity.attachments:
    if attachment.content_type == "application/vnd.microsoft.teams.file.download.info":
        # Teams file download
        base64_data = await process_image_attachment(attachment)
    elif attachment.content_type.startswith("image/"):
        # Direct image attachment
        base64_data = await process_image_attachment(attachment)

# Download from URL
image_data = await download_and_encode_image("https://example.com/image.png")
```

### Comprehensive Telemetry

Track detailed bot analytics:

```python
from teams_bot_utils.telemetry.mixpanel_telemetry import BotTelemetry

telemetry = BotTelemetry(
    token="your_mixpanel_token",
    api_secret="your_api_secret"  # Optional, for identity merging
)

# Track bot installation
telemetry.track_bot_installed(
    team_id="team123",
    user_id="user456",
    channel_id="channel789"
)

# Track commands
telemetry.track_command_used(
    user_id="user123",
    command_name="help",
    success=True
)

# Set user profiles
telemetry.set_user_profile("user123", {
    "name": "John Doe",
    "email": "john@company.com",
    "team": "Engineering"
})

# Identity merging
telemetry.merge_user_identities("user123", "alt_id456")
```

### Connection Pool Management

Efficiently manage HTTP connections:

```python
from teams_bot_utils.utils.connection_pool import get_http_client

# Get shared client
client = await get_http_client(
    base_url="https://api.service.com",
    headers={"API-Key": "secret"},
    timeout=30.0,
    client_id="my_service",
    max_connections=100,
    max_keepalive_connections=20
)

# Use client
response = await client.get("/data")

# Cleanup when shutting down
from teams_bot_utils.utils.connection_pool import close_all_clients
await close_all_clients()
```

### HTTP Client Class

For more structured API interactions:

```python
from teams_bot_utils.utils.http_client import HttpClient

class MyAPIClient(HttpClient):
    def __init__(self, api_key: str):
        super().__init__(
            base_url="https://api.myservice.com",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
            pool_key="my_api"
        )
    
    async def get_user_data(self, user_id: str):
        return await self.get(f"/users/{user_id}")
    
    async def create_record(self, data: dict):
        return await self.post("/records", json_data=data)

# Usage
api = MyAPIClient("your_api_key")
user_data = await api.get_user_data("123")
result = await api.create_record({"name": "test"})
```

## 🔧 Configuration

### Environment Variables

Set these environment variables for optimal configuration:

```bash
# Mixpanel Configuration
MIXPANEL_TOKEN=your_mixpanel_project_token
MIXPANEL_API_SECRET=your_mixpanel_api_secret

# HTTP Client Settings
HTTP_TIMEOUT=30
MAX_CONNECTIONS=100
MAX_KEEPALIVE_CONNECTIONS=20
```

### Logging

Configure logging to see detailed operation information:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Library modules use standard Python logging
logger = logging.getLogger('teams_bot_utils')
```

## 🏗️ Architecture

### Module Structure

```
teams_bot_utils/
├── extensions.py          # Activity class extensions
├── images/
│   └── processing.py      # Image processing utilities
├── telemetry/
│   └── mixpanel_telemetry.py  # Mixpanel integration
└── utils/
    ├── connection_pool.py     # Shared HTTP client pool
    └── http_client.py         # HTTP client class
```

### Key Components

1. **Activity Extensions**: Adds helper methods to Bot Framework activities
2. **Image Processing**: Handles Teams image attachments and encoding
3. **Telemetry**: Comprehensive event tracking with user identification
4. **HTTP Utilities**: Connection pooling and structured API clients

## 🚀 Performance Features

- **Connection Pooling**: Reuse HTTP connections for better performance
- **Async Operations**: Full async/await support throughout
- **Efficient Image Processing**: Streaming download and encoding
- **Lazy Initialization**: Clients created only when needed
- **Automatic Cleanup**: Built-in resource management

## 🔍 Error Handling

The library includes comprehensive error handling:

```python
try:
    image_data = await download_and_encode_image(url)
    if not image_data:
        print("Failed to download image")
except Exception as e:
    print(f"Error processing image: {e}")

# Telemetry errors are logged but don't interrupt execution
success = telemetry.track("event", "user", {"data": "value"})
if not success:
    print("Telemetry tracking failed")
```

## 🧪 Testing

```bash
# Install development dependencies
pip install teams-bot-utils[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=teams_bot_utils

# Type checking
mypy teams_bot_utils/

# Code formatting
black teams_bot_utils/
```

## 📈 Monitoring and Analytics

### Mixpanel Events

The library automatically tracks these events:

- `Bot Installed`: When bot is added to a team
- `Message Received`: When users send messages
- `Response Sent`: When bot responds
- `Command Used`: When specific commands are executed

### User Properties

Automatically collected user properties:

- `teams_id`: Microsoft Teams user ID
- `aad_id`: Azure Active Directory ID
- `email`: User email address
- `name`: Display name
- `conversation_id`: Teams conversation ID
- `platform`: Always "MS Teams"
- `$last_seen`: Last activity timestamp

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd teams-bot-utils

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **GitHub**: https://github.com/shubham7995/teams-bot-utils
- **PyPI**: https://pypi.org/project/teams-bot-utils/
- **Issues**: https://github.com/shubham7995/teams-bot-utils/issues
- **Documentation**: https://github.com/shubham7995/teams-bot-utils#readme

## 📞 Support

- **Email**: shubham.shinde@ecolab.com
- **GitHub Issues**: For bug reports and feature requests

## 🏷️ Keywords

`microsoft teams`, `bot framework`, `telemetry`, `image processing`, `http client`, `connection pooling`, `mixpanel`, `async`, `bot development`, `teams bot`

---

Built with ❤️ for the Microsoft Teams bot development community