from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import admin_required
from app.models import LowStockAlert, Product
from app.schemas import LowStockAlertOut

router = APIRouter()


@router.get("/low-stock", response_model=list[LowStockAlertOut])
def list_low_stock_alerts(db: Session = Depends(get_db), _: None = Depends(admin_required)):
    alerts = db.query(LowStockAlert).filter(LowStockAlert.resolved.is_(False)).all()
    return alerts


@router.patch("/{alert_id}/resolve", response_model=LowStockAlertOut)
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _: None = Depends(admin_required)):
    alert = db.query(LowStockAlert).get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert
