from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # like | comment | follow | ai_comment
    post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("posts.id"), nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    recipient: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    actor: Mapped["User"] = relationship("User", foreign_keys=[actor_id])
    post: Mapped[Optional["Post"]] = relationship("Post", back_populates="notifications")
