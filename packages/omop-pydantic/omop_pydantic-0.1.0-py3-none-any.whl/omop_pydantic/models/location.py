from typing import Optional
from pydantic import Field
from ..base import OmopReferenceModel


class Location(OmopReferenceModel):
    """
    OMOP CDM Location table for storing geographic location information.

    The LOCATION table represents a generic way to capture physical location or address information
    of Persons and Care Sites.
    """

    location_id: int
    address_1: Optional[str] = Field(None, max_length=50)
    address_2: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=2)
    zip: Optional[str] = Field(None, max_length=9)
    county: Optional[str] = Field(None, max_length=20)
    location_source_value: Optional[str] = Field(None, max_length=50)
