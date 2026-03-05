from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from metrics.db import get_db
from model import Order
from .schemas import OrderCreateIn, OrderOut
from service import create_order_service, get_order_service, cancel_order_service

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderOut)
def create_order(payload: OrderCreateIn, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="items is required")

    amount = sum(i.quantity * i.unit_price for i in payload.items)

    order = create_order_service(amount, payload, db)

    return order

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_service(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return order

@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = cancel_order_service(order_id, db)
    return order