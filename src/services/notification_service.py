from sqlalchemy.orm import sessionmaker, Session 
from src.configs.models import Notification

class NotificationService:
    def __init__(self, session: sessionmaker[Session]) -> None:
        self.session = session
    
    def send_notify(self, payload: Notification) -> None:
        db = self.session() 
        try:
            db.add(payload)

            db.commit()
        except Exception:
            db.rollback()
    
    def get_notifications(self):
        db = self.session()
        try:
            return db.query(Notification) \
                .order_by(Notification.id) \
                .all()
        except Exception:
            return []
        
    def delete_notification(self, id: int):
        db = self.session()
        try:
            notification = db.query(Notification).filter(Notification.id == id).first()
            
            if notification:
                db.delete(notification)

                db.commit()
        except Exception:
            db.rollback()

            