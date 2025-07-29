# Inbox4us POS Printer Service

A FastAPI-based service for handling ESC/POS printer operations. This service allows you to send base64-encoded images to network printers using the ESC/POS protocol.

## Features

- Send images to network printers
- Support for ESC/POS protocol
- Simple REST API interface
- CORS support
- SSL/TLS support

## Installation

Install using pip:

```bash
pip install inbox4us-pos-printer
```

## Usage

### Basic Usage

```python
from pos_printer import create_app
import uvicorn

app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=8100
    )
```

### With SSL

```python
from pos_printer import create_app
import uvicorn

app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=8100, 
        ssl_certfile="./ssl/certificate.crt",
        ssl_keyfile="./ssl/private.key",
        ssl_ca_certs="./ssl/ca_bundle.crt" 
    )
```

## API Documentation

### POST /print

Send an image to a network printer.

#### Request Body

```json
{
    "printer_ip": "192.168.1.100",
    "port": 9100,
    "data": "base64_encoded_image_data"
}
```

#### Parameters

- `printer_ip` (string, required): IP address of the network printer
- `port` (integer, optional, default: 9100): Printer port
- `data` (string, required): Base64 encoded image data

#### Response

Success:
```json
{
    "status": "success"
}
```

Error:
```json
{
    "status": "error",
    "message": "Error message details"
}
```

## Requirements

- Python >= 3.8
- FastAPI >= 0.68.0
- python-escpos >= 3.0
- Pillow >= 8.0.0
- pydantic >= 1.8.0
## License

MIT License

## Support

For support, please create an issue on the [GitHub repository](https://github.com/Inbox-Team/pos-printer/issues).
