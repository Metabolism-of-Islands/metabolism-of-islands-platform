-- Run this script before exporting the db. Also check trim_database URL.

-- Step 1: Create a temporary table with random first names
CREATE TEMP TABLE temp_first_names AS
SELECT unnest(ARRAY[
    'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Hannah', 'Isaac', 'Jack',
    'Liam', 'Mia', 'Noah', 'Olivia', 'Sophia', 'James', 'Ava', 'Lucas', 'Amelia', 'Logan',
    'Ella', 'Ethan', 'Chloe', 'Mason', 'Harper', 'Alexander', 'Scarlett', 'Benjamin', 'Zoe',
    'Daniel', 'Lily', 'Matthew', 'Aria', 'Henry', 'Nora', 'Jackson', 'Riley', 'Sebastian', 
    'Layla', 'Aiden', 'Sofia', 'Gabriel', 'Ellie', 'Carter', 'Mila', 'Owen', 'Victoria', 
    'Wyatt', 'Addison', 'Julian', 'Grace', 'Isaiah', 'Savannah', 'Levi', 'Aubrey', 'Samuel', 
    'Brooklyn', 'David', 'Lucy', 'Anthony', 'Claire', 'Dylan', 'Skylar', 'Jaxon', 'Bella'
]) AS name;

-- Step 2: Create a temporary table with random last names
CREATE TEMP TABLE temp_last_names AS
SELECT unnest(ARRAY[
    'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
    'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson',
    'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King',
    'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter',
    'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'
]) AS name;

-- Step 3: Update the original table with random first names and last names
WITH random_names AS (
    SELECT cp.record_ptr_id, 
           fn.name AS firstname, 
           ln.name AS lastname,
           ROW_NUMBER() OVER (ORDER BY RANDOM()) AS rn
    FROM core_people cp
    JOIN temp_first_names fn ON TRUE
    JOIN temp_last_names ln ON TRUE
)
UPDATE core_people
SET firstname = random_names.firstname,
    lastname = random_names.lastname,
    email = CONCAT(random_names.firstname, '@example.com'),
    google_scholar = NULL,
    research_interests = NULL,
    linkedin = NULL,
    researchgate = NULL,
    twitter = NULL,
    affiliation = NULL,
    website = NULL,
    user_id = NULL,
    orcid = NULL
FROM random_names
WHERE core_people.record_ptr_id = random_names.record_ptr_id;

-- Step 4: Update the core_record table with the concatenated name and set other fields to NULL
UPDATE core_record
SET name = CONCAT(cp.firstname, ' ', cp.lastname),
    description = NULL,
    image = NULL,
    description_html = NULL,
    meta_data = NULL
FROM core_people cp
WHERE core_record.id = cp.record_ptr_id;

DELETE FROM core_libraryitem_saved_by_users;
DELETE FROM auth_user;
