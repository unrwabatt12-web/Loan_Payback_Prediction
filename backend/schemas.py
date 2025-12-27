# schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

# Loan prediction schemas
class SinglePredictionRequest(BaseModel):
    applicant_name: str = Field(..., description="Name of the applicant")
    annual_income: float = Field(..., gt=0, description="Annual income in USD")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    interest_rate: float = Field(..., ge=0, le=100, description="Interest rate percentage")
    debt_to_income_ratio: float = Field(..., ge=0, le=1, description="Debt to income ratio (0-1)")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (350-850)")
    
    # Optional fields
    gender: Optional[str] = Field(None, description="Gender: Male, Female, Other")
    marital_status: Optional[str] = Field(None, description="Marital status")
    education_level: Optional[str] = Field(None, description="Education level")
    employment_status: Optional[str] = Field(None, description="Employment status")
    loan_purpose: Optional[str] = Field(None, description="Purpose of the loan")
    grade_subgrade: Optional[str] = Field(None, description="Loan grade/subgrade")

    @validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['Male', 'Female', 'Other']:
            raise ValueError('Gender must be Male, Female, or Other')
        return v

    @validator('marital_status')
    def validate_marital_status(cls, v):
        if v and v not in ['Single', 'Married', 'Divorced', 'Widowed']:
            raise ValueError('Marital status must be Single, Married, Divorced, or Widowed')
        return v

    @validator('education_level')
    def validate_education_level(cls, v):
        if v and v not in ["Bachelor's", 'High School', "Master's", 'Other', 'PhD']:
            raise ValueError("Education level must be: High School, Bachelor's, Master's, PhD, or Other")
        return v

    @validator('employment_status')
    def validate_employment_status(cls, v):
        if v and v not in ['Employed', 'Retired', 'Self-employed', 'Student', 'Unemployed']:
            raise ValueError('Employment status must be Employed, Self-employed, Student, Retired, or Unemployed')
        return v

    @validator('loan_purpose')
    def validate_loan_purpose(cls, v):
        if v and v not in ['Business', 'Car', 'Debt consolidation', 'Education', 'Home', 'Medical', 'Other', 'Vacation']:
            raise ValueError('Invalid loan purpose')
        return v

    @validator('grade_subgrade')
    def validate_grade_subgrade(cls, v):
        if v and v not in ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5', 'E1', 'E2', 'E3', 'E4', 'E5', 'F1', 'F2', 'F3', 'F4', 'F5']:
            raise ValueError('Invalid grade/subgrade')
        return v

class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="0 = Rejected, 1 = Approved")
    probability: float = Field(..., ge=0, le=1, description="Probability of approval")
    risk_score: Optional[float] = Field(None, description="Risk score (0-100)")
    rejection_reasons: Optional[List[str]] = Field(None, description="Reasons for rejection if applicable")

class BatchPredictionResult(BaseModel):
    batch_id: int
    filename: str
    total_applications: int
    approved_applications: int
    rejected_applications: int
    approval_rate: float
    processing_time_seconds: float
    results: List[dict]

class HistoryResponse(BaseModel):
    predictions: List[dict]
    total: int

class StatisticsResponse(BaseModel):
    single_predictions: dict
    batch_predictions: dict