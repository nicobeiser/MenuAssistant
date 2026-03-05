from .model import Order
from .schemas import OrderCreateIn, OrderOut
from metrics.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


def create_order_service(amount, payload: OrderCreateIn, db: Session = Depends(get_db)):
    order = Order(
        status="pending_payment",
        amount=amount,
        table_id=payload.table_id,
        items=[i.model_dump() for i in payload.items],
    )
     
    db.add(order)
    db.commit()
    db.refresh(order)

    order.external_reference = str(order.id)
    db.add(order)
    db.commit()
    db.refresh(order)



def get_order_service(db, order_id):
    order = db.query(Order).filter(Order.id == order_id).first()




def cancel_order_service(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")

    if order.status == "paid":
        raise HTTPException(status_code=409, detail="cannot cancel a paid order")

    order.status = "cancelled"
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

