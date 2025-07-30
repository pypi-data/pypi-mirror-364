from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class CareSite(OmopReferenceModel):
    """
    The CARE_SITE table contains a list of uniquely identified institutional (physical or organizational)
    units where healthcare delivery is practiced (offices, wards, hospitals, clinics, etc.).
    """

    care_site_id: int
    care_site_name: Optional[str] = Field(None, max_length=255)
    place_of_service_concept_id: Optional[int] = None
    location_id: Optional[int] = None
    care_site_source_value: Optional[str] = Field(None, max_length=50)
    place_of_service_source_value: Optional[str] = Field(None, max_length=50)
