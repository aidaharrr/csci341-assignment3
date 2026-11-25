from typing import Iterable, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import ConferenceSession, Paper, PaperAuthor, Review, Track


class ApplicationValidationError(ValueError):
    """Raised when a required application business rule is violated."""


def validate_no_self_review_for_review(db: Session, paper_id: int, reviewer_id: int) -> None:
    """
    Required Check 1a: Reject saving/updating a review if reviewer_id authored paper_id.
    Note: author_id and reviewer_id both reference app_user.user_id.
    """
    is_author = db.scalar(
        select(PaperAuthor.author_id).where(
            PaperAuthor.paper_id == paper_id,
            PaperAuthor.author_id == reviewer_id,
        ))
    if is_author is not None:
        raise ApplicationValidationError(
            f"Self-review rejected: user {reviewer_id} is an author of paper {paper_id}.")


def validate_no_self_review_for_authors(
    db: Session, paper_id: int, candidate_author_ids: Iterable[int]) -> None:
    """
    Required Check 1b: Reject changing a paper's authors if any new author already reviewed it.
    """
    author_set = set(candidate_author_ids)
    if not author_set:
        return

    existing_reviewer_ids = set(
        db.scalars(select(Review.reviewer_id).where(Review.paper_id == paper_id)).all())
    conflict = author_set & existing_reviewer_ids
    if conflict:
        raise ApplicationValidationError(
            f"Author update rejected: user(s) {sorted(conflict)} already submitted a review for paper {paper_id}.")


def validate_session_assignment(
    db: Session,
    track_id: int,
    status: str,
    session_id: Optional[int],) -> None:
    """
    Required Check 2a: If a paper is assigned to a session (session_id is not None),
    1) paper status must be 'accepted', and
    2) the paper's track and assigned session must belong to the same conference.
    Call this when creating/updating a paper's session_id, status, or track_id.
    """
    if session_id is None:
        return

    if status != "accepted":
        raise ApplicationValidationError(
            f"Session assignment rejected: paper status is '{status}', but only 'accepted' papers can be scheduled.")

    track_conf_id = db.scalar(
        select(Track.conference_id).where(Track.track_id == track_id))
    session_conf_id = db.scalar(
        select(ConferenceSession.conference_id).where(ConferenceSession.session_id == session_id))

    if track_conf_id is None:
        raise ApplicationValidationError(f"Track {track_id} does not exist.")
    if session_conf_id is None:
        raise ApplicationValidationError(f"Session {session_id} does not exist.")

    if track_conf_id != session_conf_id:
        raise ApplicationValidationError(
            f"Session assignment rejected: track {track_id} belongs to conference {track_conf_id}, "
            f"but session {session_id} belongs to conference {session_conf_id}.")


def validate_session_conference_update(
    db: Session, session_id: int, new_conference_id: int) -> None:
    """
    Required Check 2b: If a session's conference_id is changed, ensure no scheduled papers
    belong to a track from a different conference.
    """
    mismatched_papers = db.scalars(
        select(Paper.paper_id)
        .join(Track, Paper.track_id == Track.track_id)
        .where(
            Paper.session_id == session_id,
            Track.conference_id != new_conference_id,
        )
    ).all()

    if mismatched_papers:
        raise ApplicationValidationError(
            f"Session conference update rejected: scheduled paper(s) {list(mismatched_papers)} "
            f"belong to tracks outside conference {new_conference_id}.")