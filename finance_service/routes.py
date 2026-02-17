"""
Finance Service Routes
Implements financial management endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from .models import (
    Invoice, InvoiceCreate, Payment, PaymentCreate,
    Transaction, TransactionCreate, Budget, BudgetCreate,
    StudentAccount, StudentAccountWithHistory, FinancialReport
)

# Mock database
INVOICES_DB = {}
PAYMENTS_DB = {}
TRANSACTIONS_DB = {}
BUDGETS_DB = {}
ACCOUNTS_DB = {}
INVOICE_ID_COUNTER = 1000

router = APIRouter(prefix="/api/finance", tags=["Finance"])


# ===== STUDENT ACCOUNTS =====
@router.post("/accounts", response_model=StudentAccount, status_code=status.HTTP_201_CREATED)
async def create_student_account(student_id: int) -> StudentAccount:
    """
    Create a student financial account.
    
    **Best Practice**: Initialize account with zero balance and default settings
    """
    # Check if account already exists
    if any(a["student_id"] == student_id for a in ACCOUNTS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists for this student"
        )
    
    account_id = len(ACCOUNTS_DB) + 1
    new_account = {
        "id": account_id,
        "student_id": student_id,
        "balance": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    ACCOUNTS_DB[account_id] = new_account
    return StudentAccount(**new_account)


@router.get("/accounts/{student_id}", response_model=StudentAccountWithHistory)
async def get_student_account(student_id: int) -> StudentAccountWithHistory:
    """
    Get student account with transaction history.
    
    **Best Practice**: Show complete financial picture with related records
    """
    account = next((a for a in ACCOUNTS_DB.values() if a["student_id"] == student_id), None)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    invoices = [Invoice(**i) for i in INVOICES_DB.values() if i["student_id"] == student_id]
    payments = [Payment(**p) for p in PAYMENTS_DB.values() if p["invoice_id"] in [inv["id"] for inv in INVOICES_DB.values() if inv["student_id"] == student_id]]
    transactions = [Transaction(**t) for t in TRANSACTIONS_DB.values() if t["student_id"] == student_id]
    
    return StudentAccountWithHistory(
        **account,
        invoices=invoices,
        payments=payments,
        transactions=transactions
    )


# ===== INVOICES =====
@router.post("/invoices", response_model=Invoice, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: InvoiceCreate) -> Invoice:
    """
    Create an invoice for a student.
    
    **Best Practice**: Auto-generate invoice numbers and validate amounts
    """
    global INVOICE_ID_COUNTER
    
    # Validate amount
    if invoice_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice amount must be positive"
        )
    
    invoice_id = INVOICE_ID_COUNTER
    INVOICE_ID_COUNTER += 1
    
    new_invoice = {
        "id": invoice_id,
        "invoice_number": f"INV-{invoice_id}",
        "student_id": invoice_data.student_id,
        "amount": invoice_data.amount,
        "description": invoice_data.description,
        "due_date": invoice_data.due_date,
        "status": "issued",
        "created_at": datetime.utcnow()
    }
    
    INVOICES_DB[invoice_id] = new_invoice
    
    # Update student account balance
    account = next((a for a in ACCOUNTS_DB.values() if a["student_id"] == invoice_data.student_id), None)
    if account:
        account["balance"] += invoice_data.amount
        account["updated_at"] = datetime.utcnow()
    
    return Invoice(**new_invoice)


@router.get("/invoices", response_model=List[Invoice])
async def list_invoices(student_id: int = None, skip: int = 0, limit: int = 10) -> List[Invoice]:
    """List invoices with filtering and pagination."""
    invoices = list(INVOICES_DB.values())
    
    if student_id:
        invoices = [i for i in invoices if i["student_id"] == student_id]
    
    invoices = invoices[skip:skip + limit]
    return [Invoice(**i) for i in invoices]


@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int) -> Invoice:
    """Get a specific invoice."""
    invoice = INVOICES_DB.get(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return Invoice(**invoice)


# ===== PAYMENTS =====
@router.post("/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def record_payment(payment_data: PaymentCreate) -> Payment:
    """
    Record a payment for an invoice.
    
    **Best Practice**: Validate invoice exists and handle partial payments
    """
    invoice = INVOICES_DB.get(payment_data.invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Validate payment amount
    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be positive"
        )
    
    payment_id = len(PAYMENTS_DB) + 1
    new_payment = {
        "id": payment_id,
        "invoice_id": payment_data.invoice_id,
        "amount": payment_data.amount,
        "payment_method": payment_data.payment_method,
        "status": "completed",
        "payment_date": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "transaction_id": payment_data.transaction_id
    }
    
    PAYMENTS_DB[payment_id] = new_payment
    
    # Update invoice status if fully paid
    total_paid = sum(p["amount"] for p in PAYMENTS_DB.values() if p["invoice_id"] == payment_data.invoice_id)
    if total_paid >= invoice["amount"]:
        invoice["status"] = "paid"
    
    # Update account balance
    account = next((a for a in ACCOUNTS_DB.values() if a["student_id"] == invoice["student_id"]), None)
    if account:
        account["balance"] -= payment_data.amount
        account["updated_at"] = datetime.utcnow()
    
    return Payment(**new_payment)


@router.get("/payments", response_model=List[Payment])
async def list_payments(invoice_id: int = None, skip: int = 0, limit: int = 10) -> List[Payment]:
    """List payments with filtering."""
    payments = list(PAYMENTS_DB.values())
    
    if invoice_id:
        payments = [p for p in payments if p["invoice_id"] == invoice_id]
    
    payments = payments[skip:skip + limit]
    return [Payment(**p) for p in payments]


@router.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: int) -> Payment:
    """Get a specific payment."""
    payment = PAYMENTS_DB.get(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return Payment(**payment)


# ===== TRANSACTIONS =====
@router.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def record_transaction(transaction_data: TransactionCreate) -> Transaction:
    """
    Record a financial transaction.
    
    **Best Practice**: Maintain immutable transaction log for audit trail
    """
    transaction_id = len(TRANSACTIONS_DB) + 1
    ref_number = f"TXN-{transaction_id}-{datetime.utcnow().timestamp()}"
    
    new_transaction = {
        "id": transaction_id,
        "student_id": transaction_data.student_id,
        "transaction_type": transaction_data.transaction_type,
        "amount": transaction_data.amount,
        "reference_number": ref_number,
        "transaction_date": datetime.utcnow(),
        "description": transaction_data.description,
        "created_at": datetime.utcnow()
    }
    
    TRANSACTIONS_DB[transaction_id] = new_transaction
    
    # Update account balance based on transaction type
    account = next((a for a in ACCOUNTS_DB.values() if a["student_id"] == transaction_data.student_id), None)
    if account:
        if transaction_data.transaction_type == "refund":
            account["balance"] -= transaction_data.amount
        elif transaction_data.transaction_type == "scholarship":
            account["balance"] -= transaction_data.amount
        account["updated_at"] = datetime.utcnow()
    
    return Transaction(**new_transaction)


@router.get("/transactions", response_model=List[Transaction])
async def list_transactions(student_id: int = None, skip: int = 0, limit: int = 10) -> List[Transaction]:
    """List transactions with filtering and pagination."""
    transactions = list(TRANSACTIONS_DB.values())
    
    if student_id:
        transactions = [t for t in transactions if t["student_id"] == student_id]
    
    transactions = sorted(transactions, key=lambda x: x["created_at"], reverse=True)
    return [Transaction(**t) for t in transactions[skip:skip + limit]]


# ===== BUDGETS =====
@router.post("/budgets", response_model=Budget, status_code=status.HTTP_201_CREATED)
async def create_budget(budget_data: BudgetCreate) -> Budget:
    """Create a budget allocation."""
    budget_id = len(BUDGETS_DB) + 1
    new_budget = {
        "id": budget_id,
        "category": budget_data.category,
        "allocated_amount": budget_data.allocated_amount,
        "fiscal_year": budget_data.fiscal_year,
        "spent_amount": 0.0,
        "created_at": datetime.utcnow()
    }
    
    BUDGETS_DB[budget_id] = new_budget
    return Budget(**new_budget)


@router.get("/budgets", response_model=List[Budget])
async def list_budgets(fiscal_year: int = None) -> List[Budget]:
    """List budgets with optional filtering by fiscal year."""
    budgets = list(BUDGETS_DB.values())
    
    if fiscal_year:
        budgets = [b for b in budgets if b["fiscal_year"] == fiscal_year]
    
    return [Budget(**b) for b in budgets]


# ===== FINANCIAL REPORTS =====
@router.get("/reports/summary")
async def get_financial_summary() -> dict:
    """
    Get financial summary (total revenue, expenses, balance).
    
    **Best Practice**: Calculate summaries efficiently with caching
    """
    total_invoiced = sum(i["amount"] for i in INVOICES_DB.values())
    total_paid = sum(p["amount"] for p in PAYMENTS_DB.values())
    total_outstanding = total_invoiced - total_paid
    
    return {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_outstanding": total_outstanding,
        "invoice_count": len(INVOICES_DB),
        "payment_count": len(PAYMENTS_DB),
        "account_count": len(ACCOUNTS_DB)
    }


@router.get("/reports/student/{student_id}")
async def get_student_financial_report(student_id: int) -> dict:
    """Get financial report for a specific student."""
    account = next((a for a in ACCOUNTS_DB.values() if a["student_id"] == student_id), None)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    invoices = [i for i in INVOICES_DB.values() if i["student_id"] == student_id]
    payments = [p for p in PAYMENTS_DB.values() if p["invoice_id"] in [inv["id"] for inv in invoices]]
    
    total_invoiced = sum(i["amount"] for i in invoices)
    total_paid = sum(p["amount"] for p in payments)
    
    return {
        "student_id": student_id,
        "current_balance": account["balance"],
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_outstanding": total_invoiced - total_paid,
        "invoice_count": len(invoices),
        "payment_count": len(payments)
    }
