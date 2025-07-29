from wb_api.base.dataclass import BaseRequest

from pydantic.fields import Field


class Request(BaseRequest):
	id: str
	text: str = Field(min_length=2, max_length=5000)

	def as_request_payload(self):
		return self.model_dump()
