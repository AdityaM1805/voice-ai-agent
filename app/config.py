from pydantic_settings import BaseSettings

#All envonment variables are defined here and are loaded from the .env file
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DATABASE_URL: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    #Tell pydantic to load the env variables from the .env file
    class Config:
        env_file = ".env"

#create one global settings object
settings = Settings()        