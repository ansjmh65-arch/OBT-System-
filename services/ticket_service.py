from models import Ticket
from database.database import db

class TicketService:
    @staticmethod
    def create_ticket(guild_id: int, user_id: int, channel_id: int):
        ticket = Ticket(guild_id=guild_id, user_id=user_id, channel_id=channel_id, status="open")
        db.session.add(ticket)
        db.session.commit()
        return ticket

    @staticmethod
    def close_ticket(channel_id: int):
        ticket = Ticket.query.filter_by(channel_id=channel_id).first()
        if ticket:
            ticket.status = "closed"
            db.session.commit()
        return ticket
      
