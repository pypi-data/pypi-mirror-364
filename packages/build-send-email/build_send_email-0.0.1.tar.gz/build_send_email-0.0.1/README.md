# Send Email

An enhanced command-line tool for building and sending emails with multiple backend support.

## Features

- **Multiple backends**: AWS SES, SMTP, local sendmail
- **Configuration management**: YAML/JSON config files with defaults
- **Retry logic**: Exponential backoff for failed sends
- **Email validation**: Basic validation for email addresses
- **HTML support**: Send both plain text and HTML emails
- **Attachments**: Add file attachments to emails
- **Dry-run mode**: Preview what would be sent
- **Portable**: Minimal dependencies, works across projects

## Installation

### Standalone Usage
```bash
# Install the package and its dependencies
pip install -e .

# Or install optional dependencies manually
pip install boto3  # For AWS SES
pip install pyyaml # For YAML config files
```

### Integration into Another Project
```bash
# Install as a dependency
pip install /path/to/build-send-email

# Or add to pyproject.toml dependencies
# boto3>=1.26.0  # For AWS SES
# pyyaml>=6.0    # For YAML configs
```

## Configuration

Create a config file at one of these locations:
- `~/.config/build-send-email/config.yaml`
- `~/.build-send-email.yaml`
- `.build-send-email.yaml` (project-local)

See `build-send-email-config.yaml` for example configuration.

## Usage Examples

### Building Emails

```bash
# Basic email
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="Test Email" --body="Hello, World!" --output=message.eml

# Email from file with pre/post text
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="Report" --body=report.txt --body-pre="Please find the report below:" \
  --body-post="Best regards, Team" --output=message.eml

# Email with HTML content
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="HTML Email" --body=report.txt --html=report.html --output=message.eml

# Email from stdin
echo "Hello from stdin" | build-send-email build --from="sender@linaro.org" \
  --to="recipient@linaro.org" --subject="Stdin Test" --body="-"

# With attachments
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="With Attachments" --body="See attached files" \
  --attachment=file1.pdf --attachment=file2.txt --output=message.eml
```

### Sending Emails

```bash
# Send via default backend (from config)
build-send-email send message.eml

# Send via AWS SES
build-send-email send --backend=ses --aws-region=us-west-2 message.eml

# Send via SMTP
build-send-email send --backend=smtp --smtp-server=smtp.gmail.com \
  --smtp-username=user@gmail.com --smtp-password=app-password message.eml

# Send via local sendmail
build-send-email send --backend=sendmail message.eml

# Dry run (preview what would be sent)
build-send-email send --dry-run message.eml

# With retry configuration
build-send-email send --retries=5 message.eml

# Send from stdin
cat message.eml | build-send-email send -
```

### Preview Emails

```bash
# Preview email content
build-send-email preview message.eml

# Preview from stdin
cat message.eml | build-send-email preview -
```

### Combined Workflow

```bash
# Build and send in pipeline
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="Pipeline Test" --body="Hello from pipeline" | \
build-send-email send --backend=smtp --smtp-server=localhost -
```

## Backend Configuration

### AWS SES Backend
- Requires `boto3` package
- Uses AWS credentials (AWS CLI, IAM roles, or environment variables)
- Supports multiple regions and profiles

### SMTP Backend
- Works with any SMTP server (Gmail, Outlook, corporate servers)
- Supports TLS/SSL encryption
- Authentication via username/password
- **Note**: `localhost` SMTP requires a local mail server (postfix, exim) running
- For testing without a local server, use `--dry-run` flag

### Sendmail Backend
- Uses local sendmail binary
- No additional dependencies
- Good for server environments with local mail setup
- Can also work with msmtp: `--sendmail-path=/usr/bin/msmtp`

## Migration from Original Scripts

### Old build-email usage:
```bash
./build-email --msg-from="sender@linaro.org" --msg-to="recipient@linaro.org" \
  --msg-subject="Test" --msg-body=report.txt
```

### New build-send-email equivalent:
```bash
build-send-email build --from="sender@linaro.org" --to="recipient@linaro.org" \
  --subject="Test" --body=report.txt
```

### Old build-send-email usage:
```bash
./build-send-email message.eml
```

### New build-send-email equivalent:
```bash
build-send-email send --backend=ses message.eml
```

## Environment Variables

You can also configure backends via environment variables:

```bash
# AWS SES
export AWS_DEFAULT_REGION=us-west-2
export AWS_PROFILE=myprofile

# SMTP (basic)
export SMTP_SERVER=smtp.gmail.com
export SMTP_USERNAME=user@gmail.com
export SMTP_PASSWORD=app-password

# Run with env vars
build-send-email send message.eml
```

## Testing

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest
# or simply
pytest
```

## Security Notes

- Store sensitive credentials in config files with restricted permissions (`chmod 600`)
- Use environment variables or AWS IAM roles when possible
- For Gmail SMTP, use app passwords instead of account passwords
- Consider using AWS SES for production email sending

This enhanced build-send-email tool provides a unified interface for building and sending emails with multiple backend support.
