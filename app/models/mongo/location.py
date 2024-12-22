from pydantic import BaseModel, field_validator
from typing import Optional

class LocationModel(BaseModel):
    city: Optional[str]
    country: Optional[str]
    region: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    location: Optional[str]

    @field_validator('lat')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90.')
        return v

    @field_validator('lon')
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180.')
        return v
