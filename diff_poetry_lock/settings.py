import sys
from typing import Any

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    event_name: str = Field(alias="GITHUB_EVENT_NAME")  # must be 'pull_request'
    ref: str = Field(alias="GITHUB_REF")
    repository: str = Field(alias="GITHUB_REPOSITORY")
    token: str = Field(alias="INPUT_GITHUB_TOKEN")
    base_ref: str = Field(alias="github_base_ref")
    lockfile_path: str = Field(alias="input_lockfile_path", default="poetry.lock")
    api_url: str = Field(alias="github_api_url", default="https://api.github.com")

    def __init__(self, **values: Any) -> None:  # noqa: ANN401
        try:
            super().__init__(**values)
        except ValidationError as ex:
            # print validation errors to stderr
            raw_errors = ex.errors()
            for raw_e in raw_errors:
                if raw_e.get("loc", ()) == ("event_name",):
                    # event_name is not 'pull_request' - we fail early
                    print(str(raw_e), file=sys.stderr)
                    sys.exit(0)

            raise

    @field_validator("event_name")
    def event_must_be_pull_request(cls, v: str) -> str:  # noqa: N805
        if v != "pull_request":
            raise ValueError(
                "This Github Action can only be run in the context of a pull request"
            )
        return v

    def pr_num(self) -> str:
        # TODO: Validate early
        return self.ref.split("/")[2]
