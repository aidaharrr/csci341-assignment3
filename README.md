# CSCI 341 — Assignment 3: Research Conference and Paper Review Management System

- **Course:** CSCI 341 Database Systems (Fall 2026)
- **Team Members:** Aidana Zhumagul (Backend / Parts 1 & 2), [Teammate Full Name] (Web App & Deployment / Part 3)

---

## 1. Software Versions
- **Python:** 3.15 (compatible with Python 3.11+)
- **Database Management System:** PostgreSQL 15+ (Hosted on Supabase)
- **SQLAlchemy:** 2.1.9 (`>= 2.0.30`)
- **PostgreSQL Driver (`psycopg`):** 3.3.9 (`>= 3.2.0`)
- **Environment Loader (`python-dotenv`):** 1.2.4 (`>= 1.0.1`)
- **Web Framework (Part 3):** [Teammate: e.g., FastAPI / Flask]

---

## 2. Project Structure
```text
csci341-assignment3/
├── README.md                   # Documentation, schema, assumptions, and parameters
├── requirements.txt            # Python dependencies
├── database_export.sql         # Plain pg_dump export (schema, seed data, view)
├── .env.example                # Environment variable template
├── db/
│   ├── schema.sql              # DDL: 15 tables, constraints, and view
│   └── seed.sql                # Repeatable sample dataset
├── backend/
│   ├── models.py               # Shared SQLAlchemy ORM models
│   ├── validators.py           # Application validation rules (Part 1 / Part 3)
│   └── part2_operations.py     # Part 2 SQLAlchemy script (Tasks 1–8)
└── web/                        # [Teammate: Part 3 web application files]
```

---

## 3. Environment Setup & Database Restoration

### A. Local Environment Setup
1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your PostgreSQL connection string:
   ```env
   DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<dbname>
   ```

### B. Restoring the Database
- **Method 1 — From `database_export.sql` (`psql`):**
  ```bash
  psql "postgresql://<user>:<password>@<host>:5432/<dbname>" -f database_export.sql
  ```
- **Method 2 — Repeatable Python / SQLAlchemy Reset:**
  Running `python -m backend.part2_operations` automatically executes `db/schema.sql` (Task 1) and `db/seed.sql` (Task 2), dropping and recreating all tables, constraints, sequences, and the `accepted_paper_schedule` view before populating the initial dataset.

---

## 4. Running the Queries (Part 2) and Web Application (Part 3)

### Part 2: SQL Operations via Python & SQLAlchemy
Run the standalone Part 2 script from the project root:
```powershell
python -m backend.part2_operations
```
- Every task (`1`, `2`, `3.1`, `3.2`, `4.1`, `4.2`, `5.1–5.4`, `6.1–6.4`, `7`, `8`) prints its task label, bound parameters, SQL statement, and formatted output table.
- All `UPDATE` (3.1–3.2) and `DELETE` (4.1–4.2) operations display before-and-after query results and roll back their transactions so every operation executes against the original seed dataset.

### Part 3: Deployed Web Application
- **Live Application URL:** [Teammate: Insert deployed URL here]
- **Run Locally:** [Teammate: Insert command, e.g., `uvicorn web.main:app --reload`]

---

## 5. Relational Schema, Keys, and Referential Actions
The database implements all 15 relations from Appendix A in `db/schema.sql` and `backend/models.py`:

| Table | Primary Key | Foreign Keys & Referential Actions | Additional Constraints |
| :--- | :--- | :--- | :--- |
| `app_user` | `user_id` | — | `email` `UNIQUE`, `NOT NULL` on all fields |
| `author` | `author_id` | `author_id` → `app_user.user_id` (`ON DELETE CASCADE`) | `orcid` `UNIQUE` (nullable) |
| `author_research_area` | `(author_id, area_label)` | `author_id` → `author.author_id` (`ON DELETE CASCADE`) | — |
| `reviewer` | `reviewer_id` | `reviewer_id` → `app_user.user_id` (`ON DELETE CASCADE`) | `CHECK (years_experience >= 0)` |
| `reviewer_expertise` | `(reviewer_id, area_label)` | `reviewer_id` → `reviewer.reviewer_id` (`ON DELETE CASCADE`) | — |
| `conference` | `conference_id` | — | `acronym` `UNIQUE`, `CHECK (end_date >= start_date)` |
| `conference_host` | `(conference_id, host_name)` | `conference_id` → `conference.conference_id` (`ON DELETE CASCADE`) | — |
| `conference_reviewer` | `(conference_id, reviewer_id)` | `conference_id` → `conference` (`ON DELETE CASCADE`), `reviewer_id` → `reviewer` (`ON DELETE CASCADE`) | Deleting a conference never deletes independent user/reviewer records |
| `track` | `track_id` | `conference_id` → `conference` (`ON DELETE RESTRICT`), `coordinator_id` → `reviewer` (`ON DELETE RESTRICT`) | — |
| `conference_session` | `session_id` | `conference_id` → `conference` (`ON DELETE RESTRICT`), `chair_id` → `reviewer` (`ON DELETE RESTRICT`) | `CHECK (end_time > start_time)` |
| `paper` | `paper_id` | `track_id` → `track` (`ON DELETE RESTRICT`), `session_id` → `conference_session` (`ON DELETE SET NULL`) | `status` `CHECK IN ('submitted', 'under review', 'accepted', 'rejected', 'withdrawn')` |
| `paper_keyword` | `(paper_id, keyword)` | `paper_id` → `paper.paper_id` (`ON DELETE CASCADE`) | — |
| `paper_author` | `(paper_id, author_id)` | `paper_id` → `paper` (`ON DELETE CASCADE`), `author_id` → `author` (`ON DELETE RESTRICT`) | `UNIQUE (paper_id, author_position)`, `CHECK (author_position > 0)` |
| `paper_version` | `(paper_id, version_no)` | `paper_id` → `paper.paper_id` (`ON DELETE CASCADE`) | `CHECK (version_no > 0)`; gaps in `version_no` allowed |
| `review` | `review_id` | `paper_id` → `paper` (`ON DELETE CASCADE`), `reviewer_id` → `reviewer` (`ON DELETE RESTRICT`) | `UNIQUE (paper_id, reviewer_id)`, `CHECK (overall_score BETWEEN 1 AND 5)`, `CHECK (recommendation IN ('accept', 'reject'))` |

- **Database View (`accepted_paper_schedule`):** Defined in `db/schema.sql`, joining `paper`, `track`, `conference`, `conference_session`, `paper_author` (`is_corresponding = TRUE`), and `app_user` for papers with `status = 'accepted'` and `session_id IS NOT NULL`.

---

## 6. Required Checks, Optional Business Rules & Design Assumptions

### Required Application Checks (`backend/validators.py`) — Enforced
1. **Prevent Self-Reviews:** Enforced in `validate_no_self_review_for_review` (when creating/updating a review) and `validate_no_self_review_for_authors` (when updating a paper's authors). Any overlap between a paper's `author_id` list and `reviewer_id` is rejected.
2. **Validate Session Assignments:** Enforced in `validate_session_assignment` (when assigning a paper to a session or updating a paper's `status` or `track_id`) and `validate_session_conference_update` (when changing a session's `conference_id`). Only papers with `status = 'accepted'` may be scheduled, and the paper's track and session must belong to the same conference.

### Optional Assignment 1 Business Rules
- **Satisfied in Sample Data (`db/seed.sql`):** Every user has an author and/or reviewer profile; every paper has at least one author, one keyword, one version, and exactly one corresponding author (`is_corresponding = TRUE`); all track coordinators and session chairs belong to their conference's `conference_reviewer` pool.
- **Enforcement Status:** Not enforced via database triggers or composite foreign keys (per assignment specification). Single corresponding author selection is handled in the paper form workflow; all other optional rules are documented and maintained in seed data.

### Design Assumptions
- Only completed reviews are stored in `review`.
- Version numbers in `paper_version` are positive integers per paper; gaps are allowed (e.g., Paper 1 has versions `1, 2, 4`) and `MAX(version_no)` identifies the current version.
- File uploads are not stored on disk; `paper_version.file_location` stores the file path/URI string.

---

## 7. Query Parameter Values Used in Part 2
- **Task 3.1:** `email = 'arman.armanov@example.com'`, `new_phone = '+77773414141'`
- **Task 3.2:** `target_city = 'Astana'`, `astana_days = 7`, `other_days = 3`
- **Task 4.1:** `target_status = 'withdrawn'`, `email = 'amina.aminova@example.com'`
- **Task 4.2:** `target_city = 'Astana'`
- **Task 5.1:** `status = 'accepted'`
- **Task 5.2:** `pattern = '%machine learning%'`
- **Task 5.3:** `paper_id = 1`
- **Task 5.4:** `conference_id = 1`, `expertise = 'Databases'`, `min_years = 3`
- **Task 6.3:** `accepted_status = 'accepted'`
- **Task 7:** `accepted = 'accepted'`, `rejected = 'rejected'`