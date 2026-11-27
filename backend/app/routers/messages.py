"""Buyer-seller chat about a listing. Simple polling, no websockets.

A conversation = one listing + two people. A buyer always writes to the
listing's seller; the seller replies by passing receiver_id.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Listing, Message, User
from ..schemas_market import ConversationOut, MessageCreate, MessageOut

router = APIRouter(prefix="/chats", tags=["messages"])


def _other_party(listing: Listing, user: User, other_user_id: Optional[int]) -> int:
    if user.id == listing.seller_id:
        if other_user_id is None:
            raise HTTPException(400, "Seller must say which buyer (receiver_id / other_user_id)")
        if other_user_id == user.id:
            raise HTTPException(400, "You cannot message yourself")
        return other_user_id
    return listing.seller_id


@router.get("", response_model=list[ConversationOut])
def my_conversations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    msgs = (db.query(Message)
              .filter(or_(Message.sender_id == user.id, Message.receiver_id == user.id))
              .order_by(Message.id).all())
    convos: dict = {}
    for m in msgs:
        other = m.receiver_id if m.sender_id == user.id else m.sender_id
        c = convos.setdefault((m.listing_id, other), {"unread": 0})
        c["last_message"], c["last_at"] = m.body, m.created_at
        if m.receiver_id == user.id and not m.is_read:
            c["unread"] += 1
    out = [ConversationOut(listing_id=k[0], other_user_id=k[1], **v) for k, v in convos.items()]
    return sorted(out, key=lambda c: c.last_at or 0, reverse=True)


@router.get("/{listing_id}/messages", response_model=list[MessageOut])
def get_messages(listing_id: int, other_user_id: Optional[int] = None,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    other = _other_party(listing, user, other_user_id)
    msgs = (db.query(Message)
              .filter(Message.listing_id == listing_id,
                      or_(and_(Message.sender_id == user.id, Message.receiver_id == other),
                          and_(Message.sender_id == other, Message.receiver_id == user.id)))
              .order_by(Message.id).all())
    changed = False
    for m in msgs:                       # opening the chat marks incoming messages read
        if m.receiver_id == user.id and not m.is_read:
            m.is_read, changed = True, True
    if changed:
        db.commit()
    return msgs


@router.post("/{listing_id}/messages", response_model=MessageOut, status_code=201)
def send_message(listing_id: int, data: MessageCreate, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    receiver = _other_party(listing, user, data.receiver_id)
    if db.get(User, receiver) is None:
        raise HTTPException(404, "Receiver not found")
    msg = Message(listing_id=listing_id, sender_id=user.id, receiver_id=receiver,
                  body=data.body.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
