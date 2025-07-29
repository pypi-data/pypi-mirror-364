from typing import Dict, Any

from pydantic.main import BaseModel


class BaseRequest(BaseModel):
	def as_request_params(self) -> Dict[str, Any]:
		return {}

	def as_request_payload(self) -> Dict[str, Any]:
		return {}

	def as_request_headers(self) -> Dict[str, Any]:
		return {}
