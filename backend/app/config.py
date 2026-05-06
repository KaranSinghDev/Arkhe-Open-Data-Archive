from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Database
    database_url: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "zenodolite"
    postgres_user: str = "zenodolite"
    postgres_password: str = ""

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # MinIO
    minio_host: str = "minio"
    minio_port: int = 9000
    minio_root_user: str = ""
    minio_root_password: str = ""
    minio_bucket: str = "arkhe"

    # OpenSearch
    opensearch_host: str = "opensearch"
    opensearch_port: int = 9200
    opensearch_index: str = "arkhe-records"

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    # ORCID OAuth
    orcid_client_id: str = ""
    orcid_client_secret: str = ""
    orcid_redirect_uri: str = ""
    orcid_base_url: str = "https://orcid.org"

    # App
    frontend_url: str = "http://localhost"
    backend_cors_origins: str = "http://localhost,http://localhost:80,http://localhost:5173"


settings = Settings()
