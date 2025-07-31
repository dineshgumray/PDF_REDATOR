import os

# Application Config
UPLOAD_FOLDER = 'uploads'
REDACTED_FOLDER = 'redacted'
LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'app.log')
ALLOWED_EXTENSIONS = {'pdf'}

SECRET_KEY = "supersecretkey"
SESSION_LIFETIME_MINUTES = 30
LOG_LEVEL = 'INFO'

# Create folders if they do not exist
for folder in [UPLOAD_FOLDER, REDACTED_FOLDER, LOG_FOLDER]:
    os.makedirs(folder, exist_ok=True)
