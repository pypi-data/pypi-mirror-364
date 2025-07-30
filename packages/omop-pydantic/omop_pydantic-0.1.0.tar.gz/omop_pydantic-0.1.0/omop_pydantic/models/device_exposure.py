from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class DeviceExposure(OmopClinicalModel):
    """
    The DEVICE_EXPOSURE table captures information about a person's exposure to a foreign physical object
    or instrument which is used for diagnostic or therapeutic purposes. Devices include implantable
    objects, blood transfusions, medical equipment and supplies, other instruments used in medical procedures,
    and material used in clinical care.
    """

    device_exposure_id: int
    person_id: int
    device_concept_id: int
    device_exposure_start_date: date
    device_exposure_start_datetime: Optional[datetime] = None
    device_exposure_end_date: Optional[date] = None
    device_exposure_end_datetime: Optional[datetime] = None
    device_type_concept_id: int
    unique_device_id: Optional[str] = Field(None, max_length=50)
    quantity: Optional[int] = None
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    device_source_value: Optional[str] = Field(None, max_length=50)
    device_source_concept_id: Optional[int] = None
