-- Get Weekly amounts of reaction and number of unique users that are not part of the team that sent them
SELECT COUNT(*) as weekly_reactions, COUNT(DISTINCT ll.username) as distinct_users FROM linx_luser ll JOIN linx_reactions lr ON lr.user_id = ll.user_id WHERE lr.created_at BETWEEN date('now', '-7 days') AND 'now' AND ll.username NOT IN ('Sams', 'anguyen', 'mendez3800', 'Kaya');   

-- Get Weekly amounts of messaging and number of unique users besides the team that sent them
SELECT COUNT(*) as weekly_messages, COUNT(DISTINCT ll.username) as weekly_unique_messager_count FROM linx_luser ll JOIN linx_messages lm ON ll.user_id = lm.user_id WHERE lm.created_at BETWEEN date('now', '-7 days') AND 'now' AND ll.username NOT IN ('Sams', 'anguyen', 'mendez3800', 'Kaya');

--See negative reaction amounts from users
SELECT li.iid, COUNT(*) FROM linx_images li JOIN linx_reactions as lr ON li.iid = lr.iid WHERE image_type = 'general' AND lr.reaction_type = 1 GROUP BY li.iid;

-- See positive reaction amounts from users
SELECT li.iid, COUNT(*) FROM linx_images li JOIN linx_reactions as lr ON li.iid = lr.iid WHERE image_type = 'general' AND lr.reaction_type = 2 GROUP BY li.iid;


