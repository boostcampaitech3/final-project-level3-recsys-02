"""
ORM
"""

from typing import Optional
from pydantic import BaseModel


class PlaceInfoModel(BaseModel):
    placeName: str
    placeType: str
    placeAddress: str
    latitude: Optional[float]
    longitude: Optional[float]
    telephone: Optional[str]
    description: Optional[str]
    menu: Optional[dict]
    themeKeywords: Optional[list]
    agePopularity: Optional[dict]
    genderPopularity: Optional[dict]
    time: Optional[dict]
    placeMeanRating: Optional[float]
    visitReviewNum: Optional[int]
    blogReviewNum: Optional[int]
    like: Optional[dict]


class ReviewInfoModel(BaseModel):
    userHash: str
    reviewUserID: str
    placeName: str
    placeAddress: str
    reviewContent: Optional[str]
    reviewInfoScore: Optional[str]
    reviewInfoVisitDay: Optional[str]
    reviewInfoVisitCount: Optional[int]


class UserInfoModel(BaseModel):
    userHash: str
    userID: str
    reviewNum: Optional[int]
    photo: Optional[int]
    following: Optional[int]
    follower: Optional[int]
