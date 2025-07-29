from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Create an instance of your settings class
settings = Settings()
