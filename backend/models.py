import os
from datetime import date, datetime, time
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    DateTime,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/csci341",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


class AppUser(Base):
    __tablename__ = "app_user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    given_name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    affiliation: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False)

    author_profile: Mapped[Optional["Author"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False )
    
    reviewer_profile: Mapped[Optional["Reviewer"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False)


class Author(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    orcid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    user: Mapped["AppUser"] = relationship(back_populates="author_profile")
    research_areas: Mapped[list["AuthorResearchArea"]] = relationship(
        back_populates="author", cascade="all, delete-orphan")
    authorships: Mapped[list["PaperAuthor"]] = relationship(back_populates="author")


class AuthorResearchArea(Base):
    __tablename__ = "author_research_area"

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("author.author_id", ondelete="CASCADE"), primary_key=True)
    area_label: Mapped[str] = mapped_column(String(120), primary_key=True)

    author: Mapped["Author"] = relationship(back_populates="research_areas")


class Reviewer(Base):
    __tablename__ = "reviewer"
    __table_args__ = (
        CheckConstraint("years_experience >= 0", name="ck_reviewer_years_experience"),)

    reviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["AppUser"] = relationship(back_populates="reviewer_profile")
    expertise_areas: Mapped[list["ReviewerExpertise"]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="reviewer")


class ReviewerExpertise(Base):
    __tablename__ = "reviewer_expertise"

    reviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviewer.reviewer_id", ondelete="CASCADE"), primary_key=True)
    
    area_label: Mapped[str] = mapped_column(String(120), primary_key=True)

    reviewer: Mapped["Reviewer"] = relationship(back_populates="expertise_areas")


class Conference(Base):
    __tablename__ = "conference"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_conference_dates"),)

    conference_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    acronym: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    submission_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    review_deadline: Mapped[date] = mapped_column(Date, nullable=False)

    hosts: Mapped[list["ConferenceHost"]] = relationship(
        back_populates="conference", cascade="all, delete-orphan")
    
    tracks: Mapped[list["Track"]] = relationship(back_populates="conference")
    sessions: Mapped[list["ConferenceSession"]] = relationship(back_populates="conference")


class ConferenceHost(Base):
    __tablename__ = "conference_host"

    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conference.conference_id", ondelete="CASCADE"), primary_key=True)
    
    host_name: Mapped[str] = mapped_column(String(200), primary_key=True)

    conference: Mapped["Conference"] = relationship(back_populates="hosts")


class ConferenceReviewer(Base):
    __tablename__ = "conference_reviewer"

    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conference.conference_id", ondelete="CASCADE"), primary_key=True)
    
    reviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviewer.reviewer_id", ondelete="CASCADE"), primary_key=True)
    


class Track(Base):
    __tablename__ = "track"

    track_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conference.conference_id", ondelete="RESTRICT"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    research_area: Mapped[str] = mapped_column(String(120), nullable=False)
    coordinator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviewer.reviewer_id", ondelete="RESTRICT"), nullable=False)

    conference: Mapped["Conference"] = relationship(back_populates="tracks")
    papers: Mapped[list["Paper"]] = relationship(back_populates="track")


class ConferenceSession(Base):
    __tablename__ = "conference_session"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_session_times"),)

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conference_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conference.conference_id", ondelete="RESTRICT"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room_label: Mapped[str] = mapped_column(String(80), nullable=False)
    chair_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviewer.reviewer_id", ondelete="RESTRICT"), nullable=False)
    

    conference: Mapped["Conference"] = relationship(back_populates="sessions")
    papers: Mapped[list["Paper"]] = relationship(back_populates="session")


class Paper(Base):
    __tablename__ = "paper"
    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted', 'under review', 'accepted', 'rejected', 'withdrawn')",
            name="ck_paper_status",
        ),
    )

    paper_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("track.track_id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    submission_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    session_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("conference_session.session_id", ondelete="SET NULL"), nullable=True)

    track: Mapped["Track"] = relationship(back_populates="papers")
    session: Mapped[Optional["ConferenceSession"]] = relationship(back_populates="papers")
    keywords: Mapped[list["PaperKeyword"]] = relationship(
        back_populates="paper", cascade="all, delete-orphan")
    authors: Mapped[list["PaperAuthor"]] = relationship(
        back_populates="paper", cascade="all, delete-orphan")
    versions: Mapped[list["PaperVersion"]] = relationship(
        back_populates="paper", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="paper", cascade="all, delete-orphan")


class PaperKeyword(Base):
    __tablename__ = "paper_keyword"

    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.paper_id", ondelete="CASCADE"), primary_key=True)
    keyword: Mapped[str] = mapped_column(String(100), primary_key=True)

    paper: Mapped["Paper"] = relationship(back_populates="keywords")


class PaperAuthor(Base):
    __tablename__ = "paper_author"
    __table_args__ = (
        CheckConstraint("author_position > 0", name="ck_paper_author_position"),
        UniqueConstraint("paper_id", "author_position", name="uq_paper_author_position"),)

    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.paper_id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("author.author_id", ondelete="RESTRICT"), primary_key=True)
    author_position: Mapped[int] = mapped_column(Integer, nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    paper: Mapped["Paper"] = relationship(back_populates="authors")
    author: Mapped["Author"] = relationship(back_populates="authorships")


class PaperVersion(Base):
    __tablename__ = "paper_version"
    __table_args__ = (
        CheckConstraint("version_no > 0", name="ck_paper_version_no"),)

    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.paper_id", ondelete="CASCADE"), primary_key=True)
    version_no: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_location: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    change_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    paper: Mapped["Paper"] = relationship(back_populates="versions")


class Review(Base):
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint("overall_score BETWEEN 1 AND 5", name="ck_review_score"),
        CheckConstraint("recommendation IN ('accept', 'reject')", name="ck_review_recommendation"),
        UniqueConstraint("paper_id", "reviewer_id", name="uq_review_paper_reviewer"),)

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.paper_id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviewer.reviewer_id", ondelete="RESTRICT"), nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(10), nullable=False)
    comments_for_authors: Mapped[str] = mapped_column(Text, nullable=False)
    confidential_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_submission_date: Mapped[date] = mapped_column(Date, nullable=False)

    paper: Mapped["Paper"] = relationship(back_populates="reviews")
    reviewer: Mapped["Reviewer"] = relationship(back_populates="reviews")