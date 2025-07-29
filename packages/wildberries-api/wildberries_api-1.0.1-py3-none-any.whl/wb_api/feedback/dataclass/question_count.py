from wb_api.base.dataclass import BaseRequest, BaseResponse

from typing import Optional

from pydantic.fields import Field
from pydantic.config import ConfigDict
from pydantic.functional_serializers import field_serializer
from arrow import Arrow


class Request(BaseRequest):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	date_from: Optional[Arrow] = Field(default=None, serialization_alias="dateFrom")
	date_to: Optional[Arrow] = Field(default=None, serialization_alias="dateTo")
	is_answered: Optional[bool] = Field(default=None, serialization_alias="isAnswered")

	@field_serializer("date_from", "date_to", mode="plain")
	def optional_dates_must_be_optional_int(self, value: Optional[Arrow]) -> Optional[int]:
		if value is None:
			return None

		return value.int_timestamp

	@field_serializer("is_answered", mode="plain")
	def optional_bool_must_be_optional_str(self, value: Optional[bool]) -> Optional[str]:
		if value is None:
			return None

		return "true" if value else "false"

	def as_request_params(self):
		return self.model_dump(by_alias=True, exclude_none=True)


class Response(BaseResponse):
	data: int
