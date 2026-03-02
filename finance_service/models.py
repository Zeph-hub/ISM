"""
Finance Service Models
Defines Pydantic and SQLAlchemy models for financial management.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Base


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


# SQLAlchemy ORM Models
class InvoiceORM(Base):
    """Invoice ORM model"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_accounts.student_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    payments = relationship("PaymentORM", back_populates="invoice")
    account = relationship("StudentAccountORM", back_populates="invoices")


class PaymentORM(Base):
    """Payment ORM model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(100), nullable=False)
    transaction_id = Column(String(100), nullable=True, unique=True)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("InvoiceORM", back_populates="payments")


class TransactionORM(Base):
    """Transaction ORM model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_accounts.student_id"), nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    reference_number = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    account = relationship("StudentAccountORM", back_populates="transactions")


class BudgetORM(Base):
    """Budget ORM model"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(255), nullable=False, index=True)
    allocated_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)
    fiscal_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialReportORM(Base):
    """Financial Report ORM model"""
    __tablename__ = "financial_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)  # income, expense, balance_sheet
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentAccountORM(Base):
    """Student Account ORM model"""
    __tablename__ = "student_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, unique=True, nullable=False, index=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    invoices = relationship("InvoiceORM", back_populates="account")
    transactions = relationship("TransactionORM", back_populates="account")


# Pydantic Models (for API validation)



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
