"""
Finance Service Models
Defines Pydantic models for financial management.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type"""
    TUITION = "tuition"
    FEE = "fee"
    SCHOLARSHIP = "scholarship"
    REFUND = "refund"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    OVERDUE = "overdue"


class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceBase(BaseModel):
    """Base invoice model"""
    student_id: int
    amount: float
    description: str
    due_date: datetime


class InvoiceCreate(InvoiceBase):
    """Invoice creation model"""
    pass


class Invoice(InvoiceBase):
    """Invoice response model"""
    id: int
    invoice_number: str
    status: InvoiceStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    """Base payment model"""
    invoice_id: int
    amount: float
    payment_method: str  # "credit_card", "bank_transfer", "cash", etc.


class PaymentCreate(PaymentBase):
    """Payment creation model"""
    transaction_id: Optional[str] = None


class Payment(PaymentBase):
    """Payment response model"""
    id: int
    status: PaymentStatus
    payment_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base transaction model"""
    student_id: int
    transaction_type: TransactionType
    amount: float


class TransactionCreate(TransactionBase):
    """Transaction creation model"""
    description: Optional[str] = None


class Transaction(TransactionBase):
    """Transaction response model"""
    id: int
    reference_number: str
    transaction_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    """Base budget model"""
    category: str
    allocated_amount: float
    fiscal_year: int


class BudgetCreate(BudgetBase):
    """Budget creation model"""
    pass


class Budget(BudgetBase):
    """Budget response model"""
    id: int
    spent_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinancialReportBase(BaseModel):
    """Base financial report model"""
    title: str
    report_type: str  # "income", "expense", "balance_sheet", etc.
    start_date: datetime
    end_date: datetime


class FinancialReportCreate(FinancialReportBase):
    """Financial report creation model"""
    pass


class FinancialReport(FinancialReportBase):
    """Financial report response model"""
    id: int
    data: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentAccountBase(BaseModel):
    """Base student account model"""
    student_id: int
    balance: float


class StudentAccount(StudentAccountBase):
    """Student account response model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StudentAccountWithHistory(StudentAccount):
    """Student account with transaction history"""
    invoices: list[Invoice] = []
    payments: list[Payment] = []
    transactions: list[Transaction] = []
