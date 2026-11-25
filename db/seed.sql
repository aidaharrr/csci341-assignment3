-- CSCI 341 Assignment 3 - Simple Repeatable Seed Data

TRUNCATE TABLE
    review,
    paper_version,
    paper_author,
    paper_keyword,
    paper,
    conference_session,
    track,
    conference_reviewer,
    conference_host,
    conference,
    reviewer_expertise,
    reviewer,
    author_research_area,
    author,
    app_user
RESTART IDENTITY CASCADE;

--                          APP_USER 10
INSERT INTO app_user (user_id, given_name, surname, email, affiliation, country, phone_number) VALUES
(1, 'Arman', 'Armanov', 'arman.armanov@example.com', 'NU',          'Kazakhstan', '+77011111111'),
(2, 'Amina', 'Aminova', 'amina.aminova@example.com', 'KBTU',        'Kazakhstan', '+77012222222'),
(3, 'Askar', 'Amanzholov', 'askar.amanzholov@example.com', 'AITU',        'Kazakhstan', '+77013333333'),
(4, 'Aidana', 'Zhumagul', 'aidana.zhumagul@example.com', 'NU',          'Kazakhstan', '+77014444444'),
(5, 'Zhibek', 'Serikova', 'zhibek.serikova@example.com', 'KazNU',       'Kazakhstan', '+77015555555'),
(6, 'Alibi', 'Kassymov', 'alibi.kassymov@example.com', 'SDU',         'Kazakhstan', '+77016666666'),
(7, 'Nurlan', 'Bekov', 'nurlan.bekov@example.com', 'Satbayev',    'Kazakhstan', '+77017777777'),
(8, 'Dana', 'Tolegen', 'dana.tolegen@example.com', 'ENU',         'Kazakhstan', '+77018888888'),
(9, 'Madi', 'Suleimenov', 'madi.suleimenov@example.com', 'AITU',        'Kazakhstan', '+77019999999'),
(10, 'Aigerim', 'Nurlanova', 'aigerim.nurlanova@example.com','KBTU',        'Kazakhstan', '+77021010101');

--                              AUTHOR (7 authors: 2,7,9 author-only; 1,3,5,10 both roles)
INSERT INTO author (author_id, orcid) VALUES
(1, '0000-0001-0001-0001'),
(2, '0000-0001-0001-0002'),
(3, '0000-0001-0001-0003'),
(5, '0000-0001-0001-0005'),
(7, NULL),
(9, '0000-0001-0001-0009'),
(10, '0000-0001-0001-0010');

--                                       AUTHOR_RESEARCH_AREA
INSERT INTO author_research_area (author_id, area_label) VALUES
(1,  'Databases'),
(2,  'Machine Learning'),
(3,  'Databases'),
(5,  'AI'),
(7,  'Databases'),
(9,  'Networks'),
(10, 'Machine Learning');

--                   REVIEWER (7 reviewers: 4,6,8 reviewer-only; 1,3,5,10 both roles)
INSERT INTO reviewer (reviewer_id, years_experience) VALUES
(1, 6),
(3, 5),
(4, 8),
(5, 4),
(6, 2),  -- < 3 years (excluded by Query 5.4)
(8, 7),  -- 0 reviews (tests Query 6.2 and 6.4)
(10, 3);  -- exactly 3 years (included by Query 5.4)

--                                       REVIEWER_EXPERTISE
INSERT INTO reviewer_expertise (reviewer_id, area_label) VALUES
(1, 'Databases'),
(3, 'Databases'),
(3, 'AI'),
(4, 'Databases'),
(5, 'AI'),
(6, 'Databases'),
(8, 'Databases'),
(10, 'Databases'),
(10, 'Machine Learning');

--              CONFERENCE (2 in Astana, 1 in Almaty; Conf 3 has no papers)
INSERT INTO conference (conference_id, name, acronym, description, city, country, start_date, end_date, submission_deadline, review_deadline) VALUES
(1, 'Astana DB Conf', 'ADB2026', 'Database conference.', 'Astana', 'Kazakhstan', '2026-10-10', '2026-10-12', '2026-07-01', '2026-08-15'),
(2, 'Almaty AI Conf', 'AAI2026', 'AI conference.', 'Almaty', 'Kazakhstan', '2026-11-05', '2026-11-07', '2026-07-15', '2026-09-01'),
(3, 'Astana Tech Day', 'ATD2026', 'One-day tech event.', 'Astana', 'Kazakhstan', '2026-12-01', '2026-12-01', '2026-09-01', '2026-10-10');

--                                      CONFERENCE_HOST
INSERT INTO conference_host (conference_id, host_name) VALUES
(1, 'NU'),
(1, 'AITU'),
(2, 'KBTU'),
(3, 'ENU');

--                                        CONFERENCE_REVIEWER
INSERT INTO conference_reviewer (conference_id, reviewer_id) VALUES
(1, 1), (1, 3), (1, 4), (1, 5), (1, 6), (1, 8), (1, 10),
(2, 4), (2, 5), (2, 6), (2, 8), (2, 10),
(3, 1), (3, 3), (3, 10);

--                               TRACK (Tracks 3 and 5 are empty)
INSERT INTO track (track_id, conference_id, name, description, research_area, coordinator_id) VALUES
(1, 1, 'Databases', 'SQL and indexing.', 'Databases', '1'),
(2, 1, 'AI Track', 'ML applications.', 'AI', '3'),
(3, 1, 'Security', 'Data privacy.', 'Security', '4'),
(4, 2, 'Smart Data', 'Data systems.', 'AI', '5'),
(5, 3, 'Future Tech', 'New computing.', 'Systems', '10');

--                     CONFERENCE_SESSION (Session 3 is empty in Astana; Session 5 is empty in Almaty)
INSERT INTO conference_session (session_id, conference_id, title, session_date, start_time, end_time, room_label, chair_id) VALUES
(1, 1, 'DB Session', '2026-10-10', '09:00:00', '11:00:00', 'Room 101', 4),
(2, 1, 'AI Session', '2026-10-10', '13:00:00', '15:00:00', 'Room 102', 5),
(3, 1, 'Extra Session', '2026-10-11', '10:00:00', '11:30:00', 'Room 103', 1),
(4, 2, 'Main Session', '2026-11-05', '10:00:00', '12:00:00', 'Hall A',   8),
(5, 2, 'Open Session', '2026-11-06', '14:00:00', '15:00:00', 'Hall B',   6);

--              PAPER (10 papers: all 5 statuses, accepted with/without session, mixed-case ML)
INSERT INTO paper (paper_id, track_id, title, abstract, submission_date, status, session_id) VALUES
(1, 1, 'Fast SQL Indexes', 'Uses machine learning for fast index lookup.',   '2026-06-01', 'accepted',     1),
(2, 1, 'Simple Transactions', 'Easy locking method for small databases.',       '2026-06-02', 'accepted',     1),
(3, 2, 'Edge AI Models', 'Tests Machine Learning on small phones.',        '2026-06-03', 'accepted',     2),
(4, 2, 'Graph Search', 'Fast MACHINE LEARNING search on graphs.',        '2026-06-04', 'accepted',     NULL),
(5, 1, 'Basic Join Study', 'Compares simple join methods in SQL.',           '2026-06-05', 'rejected',     NULL),
(6, 2, 'Draft ML Paper', 'Early machine learning draft.',                  '2026-06-06', 'withdrawn',    NULL),
(7, 1, 'Old Table Test', 'Early database table test.',                     '2026-06-07', 'withdrawn',    NULL),
(8, 2, 'Data Cleaning', 'Finds duplicate rows in tables.',                '2026-06-08', 'under review', NULL),
(9, 1, 'Log Compression', 'Saves disk space for server logs.',              '2026-06-09', 'submitted',    NULL),
(10, 4, 'Medical AI Helper', 'Simple AI tool for clinic data.',                '2026-06-10', 'accepted',     4);

--                                  PAPER_KEYWORD
INSERT INTO paper_keyword (paper_id, keyword) VALUES
(1, 'indexing'), (1, 'sql'),
(2, 'transactions'),
(3, 'edge'), (3, 'ml'),
(4, 'graphs'),
(5, 'joins'),
(6, 'draft'),
(7, 'tables'),
(8, 'cleaning'),
(9, 'logs'),
(10, 'medical');

--                          PAPER_AUTHOR (1 corresponding author per paper; Arman & Nurlan repeat in Track 1)
INSERT INTO paper_author (paper_id, author_id, author_position, is_corresponding) VALUES
(1, 1, 1, TRUE),  (1,  7,  2, FALSE),
(2, 3, 1, TRUE),  (2,  10, 2, FALSE),
(3, 5, 1, TRUE),  (3,  9,  2, FALSE),
(4, 10, 1, TRUE),
(5, 7, 1, TRUE),  (5,  1,  2, FALSE),
(6, 2, 1, TRUE),  (6,  7,  2, FALSE), -- Amina + withdrawn (Delete 4.1)
(7, 2, 1, TRUE), -- Amina + withdrawn (Delete 4.1)
(8, 2, 1, TRUE), -- Amina + under review (kept in 4.1)
(9, 9, 1, TRUE),
(10, 5,  1, TRUE),  (10, 9,  2, FALSE);

--                    PAPER_VERSION (13 versions; Paper 1 has versions 1, 2, 4 to show allowed gap)
INSERT INTO paper_version (paper_id, version_no, file_location, uploaded_at, change_note) VALUES
(1, 1, '/files/p1_v1.pdf', '2026-06-01 10:00:00', 'First version'),
(1, 2, '/files/p1_v2.pdf', '2026-06-15 12:00:00', 'Fixed typos'),
(1, 4, '/files/p1_v4.pdf', '2026-08-20 15:00:00', 'Final version'),
(2, 1, '/files/p2_v1.pdf', '2026-06-02 10:00:00', 'First version'),
(3, 1, '/files/p3_v1.pdf', '2026-06-03 10:00:00', 'First version'),
(4, 1, '/files/p4_v1.pdf', '2026-06-04 10:00:00', 'First version'),
(5, 1, '/files/p5_v1.pdf', '2026-06-05 10:00:00', 'First version'),
(6, 1, '/files/p6_v1.pdf', '2026-06-06 10:00:00', 'First draft'),
(6, 2, '/files/p6_v2.pdf', '2026-06-08 11:00:00', 'Second draft'),
(7, 1, '/files/p7_v1.pdf', '2026-06-07 10:00:00', 'First draft'),
(8, 1, '/files/p8_v1.pdf', '2026-06-08 10:00:00', 'First version'),
(9, 1, '/files/p9_v1.pdf', '2026-06-09 10:00:00', 'First version'),
(10, 1, '/files/p10_v1.pdf', '2026-06-10 10:00:00', 'First version');

--        REVIEW (14 completed reviews; no self-reviews; avg = 14 / 7 reviewers = 2.00)
INSERT INTO review (review_id, paper_id, reviewer_id, overall_score, recommendation, comments_for_authors, confidential_comments, review_submission_date) VALUES
(1, 1, 4, 5, 'accept', 'Great results.', 'Top paper.', '2026-07-20'),
(2, 1, 3, 4, 'accept', 'Clear and useful.', NULL, '2026-07-21'),
(3, 2, 4, 5, 'accept', 'Very clean method.', 'Good work.', '2026-07-22'),
(4, 2, 1, 4, 'accept', 'Easy to follow.', NULL, '2026-07-23'),
(5, 3, 4, 4, 'accept', 'Nice phone tests.', NULL, '2026-07-24'),
(6, 3, 3, 5, 'accept', 'Strong paper.', 'Accept.', '2026-07-25'),
(7, 4, 3, 4, 'accept', 'Good graph speed.', NULL, '2026-07-26'),
(8, 4, 5, 5, 'accept', 'Nice idea.', NULL, '2026-07-27'),
(9, 5, 4, 2, 'reject', 'Too basic.', 'Weak study.', '2026-07-28'),
(10, 5, 6, 2, 'reject', 'Needs more tests.', NULL, '2026-07-29'),
(11, 6, 1, 3, 'reject', 'Not finished yet.', 'Withdrawn.', '2026-07-30'),
(12, 8, 10, 4, 'accept', 'Looks promising.', NULL, '2026-08-01'),
(13, 10, 4, 5, 'accept', 'Helpful tool.', 'Accept.', '2026-08-05'),
(14, 10, 6, 4, 'accept', 'Good clinic data.', NULL, '2026-08-06');

-- Sync sequences so future inserts in the web app start after seeded IDs
SELECT setval(pg_get_serial_sequence('app_user', 'user_id'), COALESCE((SELECT MAX(user_id) FROM app_user), 1));
SELECT setval(pg_get_serial_sequence('conference', 'conference_id'), COALESCE((SELECT MAX(conference_id) FROM conference), 1));
SELECT setval(pg_get_serial_sequence('track', 'track_id'), COALESCE((SELECT MAX(track_id) FROM track), 1));
SELECT setval(pg_get_serial_sequence('conference_session', 'session_id'), COALESCE((SELECT MAX(session_id) FROM conference_session), 1));
SELECT setval(pg_get_serial_sequence('paper', 'paper_id'), COALESCE((SELECT MAX(paper_id) FROM paper), 1));
SELECT setval(pg_get_serial_sequence('review', 'review_id'), COALESCE((SELECT MAX(review_id) FROM review), 1));