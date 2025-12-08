from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Order


def generate_order_number(db: Session) -> str:
    """
    Generate a unique order number in format: ORD-YYYYMMDD-XXXX
    where XXXX is a sequential number for the day.
    """
    today = datetime.now().date()
    date_str = today.strftime("%Y%m%d")
    
    # Get the last order number for today
    last_order = db.query(Order).filter(
        Order.order_number.like(f"ORD-{date_str}-%")
    ).order_by(Order.id.desc()).first()
    
    if last_order:
        # Extract the sequence number and increment
        try:
            sequence = int(last_order.order_number.split("-")[-1])
            sequence += 1
        except (ValueError, IndexError):
            sequence = 1
    else:
        sequence = 1
    
    # Format with zero padding (4 digits)
    order_number = f"ORD-{date_str}-{sequence:04d}"
    return order_number

