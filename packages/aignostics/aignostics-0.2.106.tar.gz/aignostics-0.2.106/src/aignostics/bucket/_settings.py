"""Settings of the bucket module."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field, PlainSerializer, SecretStr
from pydantic_settings import SettingsConfigDict

from ..utils import OpaqueSettings, __env_file__, __project_name__  # noqa: TID252


class BucketProtocol(StrEnum):
    GS = "gs"
    S3 = "s3"


class Settings(OpaqueSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_prefix=f"{__project_name__.upper()}_BUCKET_",
        extra="ignore",
        env_file=__env_file__,
        env_file_encoding="utf-8",
    )

    protocol: Annotated[
        BucketProtocol,
        Field(
            description=("Protocol to access the cloud bucket, default is gs"),
            default="gs",
        ),
    ]

    name: Annotated[
        str,
        Field(description=("Name of the cloud bucket")),
    ]

    region_name: Annotated[
        str,
        Field(description=("Region of the cloud bucket"), default="EUROPE-WEST3"),
    ]

    hmac_access_key_id: Annotated[
        SecretStr,
        PlainSerializer(func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"),
        Field(description=("HMAC access key ID of the cloud bucket")),
    ]

    hmac_secret_access_key: Annotated[
        SecretStr,
        PlainSerializer(func=OpaqueSettings.serialize_sensitive_info, return_type=str, when_used="always"),
        Field(description=("HMAC secret access key of the cloud bucket")),
    ]

    upload_signed_url_expiration_seconds: Annotated[
        int,
        Field(
            description=("Expiration time for signed URLs created and used by the Python SDK to upload to the bucket."),
            default=2
            * 60
            * 60,  # The Python SDK creates the signed upload URLs immediately before uploading, so 2h is sufficient.
            ge=60,  # Minimum expiration time is 60 seconds, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
            le=7
            * 24
            * 60
            * 60,  # Limit to 7 days as this is the max e.g. at AWS, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
        ),
    ]

    download_signed_url_expiration_seconds: Annotated[
        int,
        Field(
            description=(
                "Expiration time of the signed URLs provided by the Python SDK to the platform on submitting "
                "application runs."
            ),
            default=7 * 24 * 60 * 60,  # The platform queues application runs, so we set a gracious default of 7d.
            ge=60,  # Minimum expiration time is 60 seconds, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
            le=7
            * 24
            * 60
            * 60,  # Limit to 7 days as this is the max e.g. at AWS, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
        ),
    ]
