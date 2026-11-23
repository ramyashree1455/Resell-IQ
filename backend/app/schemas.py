from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(default="buyer", pattern="^(buyer|seller)$")


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    rating: float
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ListingCreate(BaseModel):
    category: str
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    price: float = Field(gt=0)
    location: str = ""


class ListingUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    location: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(active|sold|removed)$")


class ImageOut(BaseModel):
    id: int
    url: str
    view_type: str
    model_config = {"from_attributes": True}


class ListingOut(BaseModel):
    id: int
    seller_id: int
    category: str
    title: str
    description: str
    price: float
    location: str
    grade: Optional[str]
    grade_score: Optional[int]
    status: str
    created_at: datetime
    images: List[ImageOut] = []
    model_config = {"from_attributes": True}


# --- Friend: AI Interview & Condition Grading Schemas ---

class QuestionOption(BaseModel):
    label: str
    value: str


class InterviewQuestion(BaseModel):
    id: str
    factor: str
    question: str
    help_text: Optional[str] = None
    options: List[QuestionOption]


class InterviewQuestionsResponse(BaseModel):
    category: str
    camera_prompts: List[str]
    questions: List[InterviewQuestion]


class InterviewSubmitRequest(BaseModel):
    answers: Dict[str, Any]
    transcript: Optional[str] = ""
    defects: Optional[List[Dict[str, Any]]] = None


class ConditionReportOut(BaseModel):
    id: int
    listing_id: int
    score: int
    grade: str
    defects_json: List[Any] = []
    confidence: float
    interview_transcript: Optional[str] = ""
    model_config = {"from_attributes": True}


class GradingResultOut(BaseModel):
    score: int
    grade: str
    confidence: float
    needs_manual_review: bool
    reasons: List[str] = []
    contradictions: List[str] = []
    report: ConditionReportOut


class InterviewChatRequest(BaseModel):
    message: str = ""
    step: int = 0
    answers: Dict[str, Any] = Field(default_factory=dict)
    transcript: Optional[str] = ""
    defects: Optional[List[Dict[str, Any]]] = None


class InterviewChatResponse(BaseModel):
    reply: str
    next_step: int
    camera_prompt: Optional[str] = None
    answers: Dict[str, Any]
    contradictions: List[str] = []
    is_complete: bool = False
    transcript: str = ""


