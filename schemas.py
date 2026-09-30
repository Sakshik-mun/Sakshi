from pydantic import BaseModel, EmailStr, Field, model_validator

class RegisterIn(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)

class ProfileIn(BaseModel):
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(ge=0)
    total_emi: float = Field(ge=0)
    credit_limit: float = Field(ge=0)
    credit_used: float = Field(ge=0)
    credit_score: int = Field(ge=300, le=900)

    @model_validator(mode="after")
    def check_used(self):
        if self.credit_used > self.credit_limit:
            raise ValueError("credit_used cannot exceed credit_limit")
        return self
