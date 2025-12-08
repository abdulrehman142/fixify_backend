from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="mysql+pymysql://root:tomojelly@localhost:3306/SdaProjectDb")
    SECRET_KEY: str = Field(default="pKNutGQXqfI2EyjTVis4FXJHI4xodU5H")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

