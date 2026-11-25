from pathlib import Path
from typing import Any, Mapping, Sequence
from sqlalchemy import text

from backend.models import engine

ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT_DIR / "db" / "schema.sql"
SEED_PATH = ROOT_DIR / "db" / "seed.sql"

ALL_TABLES = [
    "app_user",
    "author",
    "author_research_area",
    "reviewer",
    "reviewer_expertise",
    "conference",
    "conference_host",
    "conference_reviewer",
    "track",
    "conference_session",
    "paper",
    "paper_keyword",
    "paper_author",
    "paper_version",
    "review",
]


def print_banner(task_label: str, description: str) -> None:
    print("\n" + "=" * 80)
    print(f"TASK {task_label}: {description}")
    print("=" * 80)


def print_sql(sql: str, params: Mapping[str, Any] | None = None) -> None:
    print("\n[SQL Statement]")
    print(sql.strip())
    if params:
        print(f"[Bound Parameters] {dict(params)}")


def print_rows(rows: Sequence[Any], headers: Sequence[str]) -> None:
    print(f"\n[Result: {len(rows)} row(s)]")
    if not rows:
        print("  (no rows)")
        return
    col_widths = [
        max(len(str(h)), *(len(str(r[i])) for r in rows))
        for i, h in enumerate(headers)
    ]
    header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print("  " + header_line)
    print("  " + sep_line)
    for r in rows:
        print("  " + " | ".join(str(r[i]).ljust(col_widths[i]) for i in range(len(headers))))


def run_select(conn, sql: str, params: Mapping[str, Any] | None = None, show_sql: bool = True) -> None:
    if show_sql:
        print_sql(sql, params)
    res = conn.execute(text(sql), params or {})
    print_rows(res.fetchall(), list(res.keys()))


# ---------------------------------------------------------------------------
# Task 1: Create statements
# ---------------------------------------------------------------------------
def task_1_create_schema() -> None:
    print_banner("1", "Create all tables, constraints, and view from db/schema.sql")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    print_sql(f"-- Executing {SCHEMA_PATH.name} ({len(schema_sql.splitlines())} lines)\n{schema_sql}")
    with engine.begin() as conn:
        conn.exec_driver_sql(schema_sql)
    print("\n[Result] Schema, constraints, and view 'accepted_paper_schedule' created successfully.")


# ---------------------------------------------------------------------------
# Task 2: Insert statements & table row counts
# ---------------------------------------------------------------------------
def task_2_seed_database() -> None:
    print_banner("2", "Populate database from db/seed.sql and display row counts")
    seed_sql = SEED_PATH.read_text(encoding="utf-8")
    print_sql(f"-- Executing {SEED_PATH.name} ({len(seed_sql.splitlines())} lines)")
    with engine.begin() as conn:
        conn.exec_driver_sql(seed_sql)

        count_sql = "UNION ALL ".join(
            f"SELECT '{tbl}' AS table_name, COUNT(*) AS row_count FROM {tbl} "
            for tbl in ALL_TABLES
        )
        run_select(conn, count_sql)


# ---------------------------------------------------------------------------
# Task 3: Update statements (with before/after and transaction rollback)
# ---------------------------------------------------------------------------
def task_3_updates() -> None:
    # 3.1 Update Arman Armanov's phone number
    print_banner("3.1", "Update phone number of Arman Armanov by email (with rollback)")
    check_sql = """
        SELECT user_id, given_name, surname, email, phone_number
        FROM app_user
        WHERE email = :email;
    """
    update_sql = """
        UPDATE app_user
        SET phone_number = :new_phone
        WHERE email = :email;
    """
    params = {"email": "arman.armanov@example.com", "new_phone": "+77773414141"}

    with engine.connect() as conn:
        tx = conn.begin()
        try:
            print("\n--- BEFORE UPDATE 3.1 ---")
            run_select(conn, check_sql, {"email": params["email"]}, show_sql=False)

            print_sql(update_sql, params)
            res = conn.execute(text(update_sql), params)
            print(f"\n[Affected Rows] {res.rowcount}")

            print("\n--- AFTER UPDATE 3.1 ---")
            run_select(conn, check_sql, {"email": params["email"]}, show_sql=False)
        finally:
            tx.rollback()
            print("\n[Transaction Rolled Back] Original seed state preserved.")

    # 3.2 Conditional update of conference review_deadline (+7 days Astana, +3 days otherwise)
    print_banner("3.2", "Extend review_deadline (+7 days Astana, +3 days otherwise) (with rollback)")
    check_conf_sql = """
        SELECT conference_id, acronym, city, review_deadline
        FROM conference
        ORDER BY conference_id;
    """
    cond_update_sql = """
        UPDATE conference
        SET review_deadline = CASE
            WHEN city = :target_city THEN review_deadline + (:astana_days * INTERVAL '1 day')
            ELSE review_deadline + (:other_days * INTERVAL '1 day')
        END;
    """
    cond_params = {"target_city": "Astana", "astana_days": 7, "other_days": 3}

    with engine.connect() as conn:
        tx = conn.begin()
        try:
            print("\n--- BEFORE UPDATE 3.2 ---")
            run_select(conn, check_conf_sql, show_sql=False)

            print_sql(cond_update_sql, cond_params)
            res = conn.execute(text(cond_update_sql), cond_params)
            print(f"\n[Affected Rows] {res.rowcount}")

            print("\n--- AFTER UPDATE 3.2 ---")
            run_select(conn, check_conf_sql, show_sql=False)
        finally:
            tx.rollback()
            print("\n[Transaction Rolled Back] Original seed state preserved.")


# ---------------------------------------------------------------------------
# Task 4: Delete statements (with before/after and transaction rollback)
# ---------------------------------------------------------------------------
def task_4_deletes() -> None:
    # 4.1 Delete withdrawn papers where corresponding author is Amina Aminova
    print_banner("4.1", "Delete withdrawn papers with corresponding author Amina Aminova (with rollback)")
    inspect_sql = """
        SELECT
            (SELECT COUNT(*) FROM paper) AS papers,
            (SELECT COUNT(*) FROM paper_author) AS paper_authors,
            (SELECT COUNT(*) FROM paper_keyword) AS paper_keywords,
            (SELECT COUNT(*) FROM paper_version) AS paper_versions,
            (SELECT COUNT(*) FROM review) AS reviews,
            (SELECT COUNT(*) FROM app_user) AS users,
            (SELECT COUNT(*) FROM track) AS tracks,
            (SELECT COUNT(*) FROM conference) AS conferences;
    """
    amina_papers_sql = """
        SELECT p.paper_id, p.title, p.status, u.email AS corresponding_author
        FROM paper p
        JOIN paper_author pa ON p.paper_id = pa.paper_id AND pa.is_corresponding = TRUE
        JOIN app_user u ON pa.author_id = u.user_id
        WHERE u.email = :email
        ORDER BY p.paper_id;
    """
    delete_papers_sql = """
        DELETE FROM paper
        WHERE status = :target_status
          AND paper_id IN (
              SELECT pa.paper_id
              FROM paper_author pa
              JOIN app_user u ON pa.author_id = u.user_id
              WHERE pa.is_corresponding = TRUE
                AND u.email = :email
          );
    """
    del_params = {"target_status": "withdrawn", "email": "amina.aminova@example.com"}

    with engine.connect() as conn:
        tx = conn.begin()
        try:
            print("\n--- BEFORE DELETE 4.1 (Table Counts & Amina's Papers) ---")
            run_select(conn, inspect_sql, show_sql=False)
            run_select(conn, amina_papers_sql, {"email": del_params["email"]}, show_sql=False)

            print_sql(delete_papers_sql, del_params)
            res = conn.execute(text(delete_papers_sql), del_params)
            print(f"\n[Affected Paper Rows] {res.rowcount} (cascaded to paper_author, paper_keyword, paper_version, review)")

            print("\n--- AFTER DELETE 4.1 (Table Counts & Remaining Amina Papers) ---")
            run_select(conn, inspect_sql, show_sql=False)
            run_select(conn, amina_papers_sql, {"email": del_params["email"]}, show_sql=False)
        finally:
            tx.rollback()
            print("\n[Transaction Rolled Back] Original seed state preserved.")

    # 4.2 Delete empty sessions belonging to conferences held in Astana
    print_banner("4.2", "Delete empty sessions in Astana conferences (with rollback)")
    sessions_check_sql = """
        SELECT cs.session_id, cs.title, c.acronym, c.city, COUNT(p.paper_id) AS assigned_papers
        FROM conference_session cs
        JOIN conference c ON cs.conference_id = c.conference_id
        LEFT JOIN paper p ON cs.session_id = p.session_id
        GROUP BY cs.session_id, cs.title, c.acronym, c.city
        ORDER BY cs.session_id;
    """
    delete_sessions_sql = """
        DELETE FROM conference_session cs
        USING conference c
        WHERE cs.conference_id = c.conference_id
          AND c.city = :target_city
          AND NOT EXISTS (
              SELECT 1
              FROM paper p
              WHERE p.session_id = cs.session_id
          );
    """
    sess_params = {"target_city": "Astana"}

    with engine.connect() as conn:
        tx = conn.begin()
        try:
            print("\n--- BEFORE DELETE 4.2 ---")
            run_select(conn, sessions_check_sql, show_sql=False)

            print_sql(delete_sessions_sql, sess_params)
            res = conn.execute(text(delete_sessions_sql), sess_params)
            print(f"\n[Affected Session Rows] {res.rowcount}")

            print("\n--- AFTER DELETE 4.2 ---")
            run_select(conn, sessions_check_sql, show_sql=False)
        finally:
            tx.rollback()
            print("\n[Transaction Rolled Back] Original seed state preserved.")


# ---------------------------------------------------------------------------
# Task 5: Simple queries
# ---------------------------------------------------------------------------
def task_5_simple_queries() -> None:
    with engine.connect() as conn:
        # 5.1 Accepted papers with corresponding author, track, and conference
        print_banner("5.1", "List accepted papers with corresponding author, track, and conference")
        q51 = """
            SELECT
                p.paper_id,
                p.title,
                (u.given_name || ' ' || u.surname) AS corresponding_author_name,
                u.email AS corresponding_author_email,
                t.name AS track_name,
                c.conference_id,
                c.acronym AS conference_acronym
            FROM paper p
            JOIN paper_author pa
                ON p.paper_id = pa.paper_id AND pa.is_corresponding = TRUE
            JOIN app_user u
                ON pa.author_id = u.user_id
            JOIN track t
                ON p.track_id = t.track_id
            JOIN conference c
                ON t.conference_id = c.conference_id
            WHERE p.status = :status
            ORDER BY p.paper_id;
        """
        run_select(conn, q51, {"status": "accepted"})

        # 5.2 Case-insensitive search for 'machine learning' in abstract
        print_banner("5.2", "Papers whose abstract contains 'machine learning' (case-insensitive)")
        q52 = """
            SELECT paper_id, title
            FROM paper
            WHERE abstract ILIKE :pattern
            ORDER BY paper_id;
        """
        run_select(conn, q52, {"pattern": "%machine learning%"})

        # 5.3 Versions for a selected paper ordered highest to lowest
        print_banner("5.3", "Versions for a selected paper ordered by version_no DESC")
        q53 = """
            SELECT version_no, file_location, uploaded_at
            FROM paper_version
            WHERE paper_id = :paper_id
            ORDER BY version_no DESC;
        """
        run_select(conn, q53, {"paper_id": 1})

        # 5.4 Reviewers in a conference pool with Databases expertise and >= 3 years experience
        print_banner("5.4", "Qualified reviewers in conference pool (Databases, >= 3 yrs experience)")
        q54 = """
            SELECT DISTINCT
                u.user_id AS reviewer_id,
                (u.given_name || ' ' || u.surname) AS full_name,
                u.email
            FROM conference_reviewer cr
            JOIN reviewer r
                ON cr.reviewer_id = r.reviewer_id
            JOIN app_user u
                ON r.reviewer_id = u.user_id
            JOIN reviewer_expertise re
                ON r.reviewer_id = re.reviewer_id
            WHERE cr.conference_id = :conference_id
              AND re.area_label = :expertise
              AND r.years_experience >= :min_years
            ORDER BY u.user_id;
        """
        run_select(conn, q54, {"conference_id": 1, "expertise": "Databases", "min_years": 3})


# ---------------------------------------------------------------------------
# Task 6: Complex queries
# ---------------------------------------------------------------------------
def task_6_complex_queries() -> None:
    with engine.connect() as conn:
        # 6.1 Distinct papers and distinct authors per track (including empty tracks)
        print_banner("6.1", "Track report: distinct papers and distinct authors (including 0-paper tracks)")
        q61 = """
            SELECT
                t.track_id,
                t.name AS track_name,
                t.conference_id,
                COUNT(DISTINCT p.paper_id) AS distinct_papers,
                COUNT(DISTINCT pa.author_id) AS distinct_authors
            FROM track t
            LEFT JOIN paper p
                ON t.track_id = p.track_id
            LEFT JOIN paper_author pa
                ON p.paper_id = pa.paper_id
            GROUP BY t.track_id, t.name, t.conference_id
            ORDER BY t.track_id;
        """
        run_select(conn, q61)

        # 6.2 Completed reviews count and average score per reviewer (including 0-review reviewers)
        print_banner("6.2", "Reviewer report: completed review count and average score")
        q62 = """
            SELECT
                r.reviewer_id,
                (u.given_name || ' ' || u.surname) AS full_name,
                COUNT(rev.review_id) AS completed_reviews,
                ROUND(AVG(rev.overall_score), 2) AS avg_overall_score
            FROM reviewer r
            JOIN app_user u
                ON r.reviewer_id = u.user_id
            LEFT JOIN review rev
                ON r.reviewer_id = rev.reviewer_id
            GROUP BY r.reviewer_id, u.given_name, u.surname
            ORDER BY r.reviewer_id;
        """
        run_select(conn, q62)

        # 6.3 Conference paper counts and average review score (without join multiplication)
        print_banner("6.3", "Conference report: total papers, accepted papers, and avg review score")
        q63 = """
            SELECT
                c.conference_id,
                c.acronym,
                COUNT(DISTINCT p.paper_id) AS total_papers,
                COUNT(DISTINCT CASE WHEN p.status = :accepted_status THEN p.paper_id END) AS accepted_papers,
                ROUND(AVG(rev.overall_score), 2) AS avg_overall_score
            FROM conference c
            LEFT JOIN track t
                ON c.conference_id = t.conference_id
            LEFT JOIN paper p
                ON t.track_id = p.track_id
            LEFT JOIN review rev
                ON p.paper_id = rev.paper_id
            GROUP BY c.conference_id, c.acronym
            ORDER BY c.conference_id;
        """
        run_select(conn, q63, {"accepted_status": "accepted"})

        # 6.4 Reviewers with review count strictly above database-wide reviewer average
        print_banner("6.4", "Reviewers with completed reviews above overall reviewer average (CTE)")
        q64 = """
            WITH reviewer_counts AS (
                SELECT
                    r.reviewer_id,
                    (u.given_name || ' ' || u.surname) AS full_name,
                    COUNT(rev.review_id) AS review_count
                FROM reviewer r
                JOIN app_user u
                    ON r.reviewer_id = u.user_id
                LEFT JOIN review rev
                    ON r.reviewer_id = rev.reviewer_id
                GROUP BY r.reviewer_id, u.given_name, u.surname
            ),
            overall_avg AS (
                SELECT AVG(review_count) AS avg_reviews_per_reviewer
                FROM reviewer_counts
            )
            SELECT
                rc.reviewer_id,
                rc.full_name,
                rc.review_count,
                ROUND(oa.avg_reviews_per_reviewer, 2) AS overall_average
            FROM reviewer_counts rc
            CROSS JOIN overall_avg oa
            WHERE rc.review_count > oa.avg_reviews_per_reviewer
            ORDER BY rc.review_count DESC, rc.reviewer_id;
        """
        run_select(conn, q64)


# ---------------------------------------------------------------------------
# Task 7: Query with a derived attribute (Acceptance rate)
# ---------------------------------------------------------------------------
def task_7_acceptance_rate() -> None:
    print_banner("7", "Conference acceptance rate percentage (derived attribute)")
    q7 = """
        SELECT
            c.conference_id,
            c.acronym,
            COUNT(CASE WHEN p.status = :accepted THEN 1 END) AS accepted_count,
            COUNT(CASE WHEN p.status = :rejected THEN 1 END) AS rejected_count,
            ROUND(
                100.0 * COUNT(CASE WHEN p.status = :accepted THEN 1 END)
                / NULLIF(
                    COUNT(CASE WHEN p.status IN (:accepted, :rejected) THEN 1 END),
                    0
                ),
                2
            ) AS acceptance_rate_pct
        FROM conference c
        LEFT JOIN track t
            ON c.conference_id = t.conference_id
        LEFT JOIN paper p
            ON t.track_id = p.track_id
        GROUP BY c.conference_id, c.acronym
        ORDER BY c.conference_id;
    """
    with engine.connect() as conn:
        run_select(conn, q7, {"accepted": "accepted", "rejected": "rejected"})


# ---------------------------------------------------------------------------
# Task 8: View operation (accepted_paper_schedule)
# ---------------------------------------------------------------------------
def task_8_view_schedule() -> None:
    print_banner("8", "Query database view accepted_paper_schedule")
    q8 = """
        SELECT
            paper_id,
            paper_title,
            conference_id,
            conference_acronym,
            track_name,
            session_id,
            session_title,
            session_date,
            start_time,
            end_time,
            room_label,
            chair_full_name,
            corresponding_author_full_name,
            corresponding_author_email
        FROM accepted_paper_schedule
        ORDER BY conference_id, session_date, start_time, session_id, paper_id;
    """
    with engine.connect() as conn:
        run_select(conn, q8)


def main() -> None:
    task_1_create_schema()
    task_2_seed_database()
    task_3_updates()
    task_4_deletes()
    task_5_simple_queries()
    task_6_complex_queries()
    task_7_acceptance_rate()
    task_8_view_schedule()
    print("\nAll Part 2 tasks (1 through 8) completed cleanly.")


if __name__ == "__main__":
    main()