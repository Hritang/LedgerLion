from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    google_service_account_file: str = "service-account.json"
    google_sheet_id: str = ""
    max_upload_mb: int = 10
    currency_default: str = "INR"
    export_dir: str = "exports"
    nonilion_bot_token: str = ""
    webhook_secret: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
