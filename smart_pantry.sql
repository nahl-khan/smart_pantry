CREATE DATABASE IF NOT EXISTS smart_pantry;
USE smart_pantry;

CREATE TABLE pantry (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    quantity DOUBLE NOT NULL,
    unit VARCHAR(50),
    expiry_date DATE,
    added_date DATE DEFAULT (CURRENT_DATE)
);

SHOW TABLES;
INSERT INTO pantry (name, category, quantity, unit, expiry_date)
VALUES
  ('milk', 'dairy', 1.0, 'liter', '2026-03-28'),
  ('tomato', 'vegetable', 4, 'pieces', '2026-03-27');

SELECT * FROM pantry;

USE smart_pantry;
INSERT INTO pantry (name, category, quantity, unit, expiry_date) VALUES
  ('eggs', 'dairy', 12, 'pieces', '2026-04-02'),
  ('butter', 'dairy', 200, 'grams', '2026-04-10'),
  ('cheddar cheese', 'dairy', 300, 'grams', '2026-04-20'),
  ('yogurt', 'dairy', 500, 'grams', '2026-03-30'),
  ('cream', 'dairy', 250, 'ml', '2026-04-05'),
  ('mozzarella', 'dairy', 250, 'grams', '2026-04-18'),
  ('parmesan', 'dairy', 150, 'grams', '2026-05-15'),
  ('paneer', 'dairy', 400, 'grams', '2026-04-07'),

  ('chicken breast', 'protein', 800, 'grams', '2026-03-29'),
  ('chicken thighs', 'protein', 1.2, 'kg', '2026-04-01'),
  ('ground beef', 'protein', 1.0, 'kg', '2026-04-03'),
  ('pork chops', 'protein', 900, 'grams', '2026-04-04'),
  ('salmon fillet', 'protein', 600, 'grams', '2026-03-28'),
  ('tilapia fillets', 'protein', 700, 'grams', '2026-03-31'),
  ('tofu firm', 'protein', 400, 'grams', '2026-04-06'),
  ('tempeh', 'protein', 300, 'grams', '2026-04-08'),
  ('lentils red', 'legume', 1.0, 'kg', '2027-01-10'),
  ('lentils green', 'legume', 1.0, 'kg', '2027-01-12'),

  ('kidney beans canned', 'legume', 3, 'cans', '2027-06-01'),
  ('black beans canned', 'legume', 4, 'cans', '2027-05-20'),
  ('chickpeas dried', 'legume', 1.5, 'kg', '2027-02-15'),
  ('chickpeas canned', 'legume', 5, 'cans', '2027-05-30'),
  ('white beans canned', 'legume', 2, 'cans', '2027-04-25'),
  ('edamame frozen', 'legume', 800, 'grams', '2027-01-05'),
  ('peas frozen', 'vegetable', 1.0, 'kg', '2027-02-01'),
  ('corn frozen', 'vegetable', 1.0, 'kg', '2027-02-10'),
  ('mixed vegetables frozen', 'vegetable', 1.0, 'kg', '2027-03-01'),

  ('onion yellow', 'vegetable', 6, 'pieces', '2026-04-25'),
  ('onion red', 'vegetable', 4, 'pieces', '2026-04-20'),
  ('garlic', 'vegetable', 5, 'bulbs', '2026-05-05'),
  ('potato', 'vegetable', 5.0, 'kg', '2026-05-15'),
  ('sweet potato', 'vegetable', 2.0, 'kg', '2026-04-30'),
  ('carrot', 'vegetable', 1.5, 'kg', '2026-04-18'),
  ('broccoli', 'vegetable', 2, 'heads', '2026-03-30'),
  ('cauliflower', 'vegetable', 1, 'head', '2026-04-01'),
  ('spinach fresh', 'vegetable', 300, 'grams', '2026-03-27'),
  ('kale', 'vegetable', 250, 'grams', '2026-03-29'),

  ('lettuce romaine', 'vegetable', 2, 'heads', '2026-03-28'),
  ('bell pepper red', 'vegetable', 3, 'pieces', '2026-04-01'),
  ('bell pepper green', 'vegetable', 3, 'pieces', '2026-04-02'),
  ('bell pepper yellow', 'vegetable', 2, 'pieces', '2026-04-03'),
  ('cucumber', 'vegetable', 4, 'pieces', '2026-03-31'),
  ('zucchini', 'vegetable', 4, 'pieces', '2026-04-04'),
  ('eggplant', 'vegetable', 3, 'pieces', '2026-04-06'),
  ('mushrooms button', 'vegetable', 400, 'grams', '2026-03-28'),
  ('mushrooms cremini', 'vegetable', 300, 'grams', '2026-03-29'),

  ('apple', 'fruit', 10, 'pieces', '2026-04-20'),
  ('banana', 'fruit', 8, 'pieces', '2026-03-27'),
  ('orange', 'fruit', 8, 'pieces', '2026-04-10'),
  ('lemon', 'fruit', 6, 'pieces', '2026-04-15'),
  ('lime', 'fruit', 6, 'pieces', '2026-04-12'),
  ('grapes', 'fruit', 500, 'grams', '2026-04-05'),
  ('strawberries', 'fruit', 400, 'grams', '2026-03-29'),
  ('blueberries', 'fruit', 300, 'grams', '2026-03-30'),
  ('raspberries', 'fruit', 250, 'grams', '2026-03-28'),
  ('pineapple', 'fruit', 1, 'piece', '2026-04-08'),

  ('watermelon', 'fruit', 1, 'piece', '2026-04-15'),
  ('mango', 'fruit', 4, 'pieces', '2026-04-05'),
  ('avocado', 'fruit', 4, 'pieces', '2026-03-27'),
  ('pear', 'fruit', 6, 'pieces', '2026-04-07'),
  ('kiwi', 'fruit', 8, 'pieces', '2026-04-06'),
  ('peach', 'fruit', 6, 'pieces', '2026-06-01'),
  ('plum', 'fruit', 6, 'pieces', '2026-06-05'),
  ('cherries', 'fruit', 300, 'grams', '2026-05-25'),
  ('pomegranate', 'fruit', 2, 'pieces', '2026-05-10'),
  ('canned pineapple', 'fruit', 2, 'cans', '2027-01-01'),

  ('rice basmati', 'grain', 5.0, 'kg', '2028-01-01'),
  ('rice jasmine', 'grain', 2.0, 'kg', '2028-02-01'),
  ('rice brown', 'grain', 2.5, 'kg', '2028-03-01'),
  ('quinoa', 'grain', 1.5, 'kg', '2028-04-01'),
  ('bulgur', 'grain', 1.0, 'kg', '2028-05-01'),
  ('couscous', 'grain', 1.0, 'kg', '2028-05-10'),
  ('oats rolled', 'grain', 2.0, 'kg', '2028-01-15'),
  ('oats instant', 'grain', 1.0, 'kg', '2028-01-20'),
  ('cornmeal', 'grain', 1.0, 'kg', '2028-02-10'),
  ('polenta', 'grain', 1.0, 'kg', '2028-02-15'),

  ('pasta spaghetti', 'grain', 2.0, 'kg', '2027-12-01'),
  ('pasta penne', 'grain', 2.0, 'kg', '2027-12-05'),
  ('pasta fusilli', 'grain', 1.5, 'kg', '2027-11-20'),
  ('pasta macaroni', 'grain', 1.5, 'kg', '2027-11-25'),
  ('noodles egg', 'grain', 1.0, 'kg', '2027-10-10'),
  ('rice noodles', 'grain', 1.0, 'kg', '2027-10-15'),
  ('lasagna sheets', 'grain', 1.0, 'kg', '2027-09-30'),
  ('bread whole wheat', 'bakery', 1, 'loaf', '2026-03-27'),
  ('bread sourdough', 'bakery', 1, 'loaf', '2026-03-28'),

  ('burger buns', 'bakery', 8, 'pieces', '2026-03-29'),
  ('tortillas wheat', 'bakery', 12, 'pieces', '2026-04-05'),
  ('tortillas corn', 'bakery', 12, 'pieces', '2026-04-10'),
  ('naan', 'bakery', 6, 'pieces', '2026-03-30'),
  ('pita bread', 'bakery', 8, 'pieces', '2026-04-03'),
  ('bagels', 'bakery', 6, 'pieces', '2026-03-29'),
  ('croissants', 'bakery', 6, 'pieces', '2026-03-27'),
  ('wraps spinach', 'bakery', 8, 'pieces', '2026-04-07'),
  ('wraps tomato basil', 'bakery', 8, 'pieces', '2026-04-08'),

  ('olive oil', 'oil', 1.0, 'liter', '2027-12-31'),
  ('canola oil', 'oil', 1.0, 'liter', '2027-11-30'),
  ('sunflower oil', 'oil', 1.0, 'liter', '2027-11-15'),
  ('sesame oil', 'oil', 500, 'ml', '2027-10-01'),
  ('coconut oil', 'oil', 800, 'ml', '2027-10-15'),
  ('ghee', 'oil', 500, 'grams', '2027-09-01'),
  ('butter clarified', 'oil', 400, 'grams', '2027-09-10'),
  ('mayonnaise', 'condiment', 400, 'grams', '2026-08-01'),
  ('ketchup', 'condiment', 500, 'grams', '2027-01-01'),
  ('mustard', 'condiment', 300, 'grams', '2027-03-01'),

  ('soy sauce', 'condiment', 500, 'ml', '2028-01-01'),
  ('fish sauce', 'condiment', 300, 'ml', '2027-12-01'),
  ('sriracha', 'condiment', 400, 'ml', '2027-06-01'),
  ('barbecue sauce', 'condiment', 500, 'ml', '2027-05-01'),
  ('hot sauce', 'condiment', 200, 'ml', '2027-04-01'),
  ('vinegar white', 'condiment', 1.0, 'liter', '2029-01-01'),
  ('vinegar apple cider', 'condiment', 750, 'ml', '2029-01-01'),
  ('vinegar balsamic', 'condiment', 500, 'ml', '2029-01-01'),
  ('pickles dill', 'condiment', 700, 'grams', '2027-03-15'),
  ('jalapenos pickled', 'condiment', 400, 'grams', '2027-03-20'),

  ('salt', 'spice', 1.0, 'kg', '2030-01-01'),
  ('black pepper ground', 'spice', 200, 'grams', '2029-06-01'),
  ('black peppercorns', 'spice', 200, 'grams', '2029-06-01'),
  ('cumin powder', 'spice', 150, 'grams', '2029-05-01'),
  ('coriander powder', 'spice', 150, 'grams', '2029-05-10'),
  ('turmeric powder', 'spice', 150, 'grams', '2029-04-01'),
  ('chili powder', 'spice', 150, 'grams', '2029-04-10'),
  ('paprika', 'spice', 150, 'grams', '2029-03-15'),
  ('oregano dried', 'spice', 100, 'grams', '2029-02-01'),
  ('basil dried', 'spice', 100, 'grams', '2029-02-10'),

  ('thyme dried', 'spice', 100, 'grams', '2029-02-15'),
  ('rosemary dried', 'spice', 100, 'grams', '2029-02-20'),
  ('garam masala', 'spice', 150, 'grams', '2029-03-01'),
  ('curry powder', 'spice', 150, 'grams', '2029-03-05'),
  ('fennel seeds', 'spice', 120, 'grams', '2029-04-05'),
  ('mustard seeds', 'spice', 120, 'grams', '2029-04-10'),
  ('cardamom pods', 'spice', 80, 'grams', '2029-05-20'),
  ('cloves whole', 'spice', 80, 'grams', '2029-05-25'),
  ('cinnamon sticks', 'spice', 80, 'grams', '2029-06-10'),
  ('nutmeg whole', 'spice', 60, 'grams', '2029-06-15'),

  ('sugar white', 'baking', 3.0, 'kg', '2029-12-31'),
  ('sugar brown', 'baking', 2.0, 'kg', '2029-11-30'),
  ('honey', 'baking', 1.0, 'kg', '2029-10-31'),
  ('maple syrup', 'baking', 750, 'ml', '2029-09-30'),
  ('flour all-purpose', 'baking', 5.0, 'kg', '2028-12-31'),
  ('flour whole wheat', 'baking', 3.0, 'kg', '2028-11-30'),
  ('baking powder', 'baking', 200, 'grams', '2028-10-31'),
  ('baking soda', 'baking', 200, 'grams', '2028-10-31'),
  ('yeast dry', 'baking', 100, 'grams', '2028-09-30'),
  ('cocoa powder', 'baking', 250, 'grams', '2028-08-31'),

  ('chocolate chips dark', 'baking', 500, 'grams', '2028-07-31'),
  ('chocolate chips milk', 'baking', 500, 'grams', '2028-07-31'),
  ('nuts almonds', 'snack', 500, 'grams', '2027-12-31'),
  ('nuts cashews', 'snack', 500, 'grams', '2027-12-31'),
  ('nuts walnuts', 'snack', 400, 'grams', '2027-11-30'),
  ('seeds sunflower', 'snack', 300, 'grams', '2027-11-15'),
  ('seeds pumpkin', 'snack', 300, 'grams', '2027-11-20'),
  ('granola', 'snack', 1.0, 'kg', '2027-10-31'),
  ('crackers whole wheat', 'snack', 400, 'grams', '2027-09-30'),
  ('rice cakes', 'snack', 300, 'grams', '2027-09-15'),

  ('frozen pizza', 'frozen', 2, 'pieces', '2027-03-31'),
  ('frozen fries', 'frozen', 1.0, 'kg', '2027-04-30'),
  ('frozen chicken nuggets', 'frozen', 1.0, 'kg', '2027-04-15'),
  ('frozen veggie burgers', 'frozen', 800, 'grams', '2027-05-01'),
  ('frozen berries mix', 'frozen', 700, 'grams', '2027-05-10'),
  ('frozen spinach', 'frozen', 600, 'grams', '2027-05-20'),
  ('ice cream vanilla', 'frozen', 1.0, 'liter', '2026-09-01'),
  ('ice cream chocolate', 'frozen', 1.0, 'liter', '2026-09-05'),
  ('frozen dumplings', 'frozen', 1.0, 'kg', '2027-06-01'),
  ('frozen peas and carrots', 'frozen', 1.0, 'kg', '2027-06-10'),

  ('coffee beans', 'beverage', 1.0, 'kg', '2028-06-01'),
  ('ground coffee', 'beverage', 500, 'grams', '2028-05-01'),
  ('black tea bags', 'beverage', 100, 'pieces', '2028-04-01'),
  ('green tea bags', 'beverage', 100, 'pieces', '2028-04-10'),
  ('herbal tea mix', 'beverage', 80, 'pieces', '2028-03-31'),
  ('orange juice', 'beverage', 2.0, 'liters', '2026-03-29'),
  ('apple juice', 'beverage', 2.0, 'liters', '2026-04-01'),
  ('sparkling water', 'beverage', 6, 'bottles', '2027-01-01'),
  ('cola', 'beverage', 6, 'cans', '2027-02-01'),
  ('tonic water', 'beverage', 6, 'cans', '2027-02-10');

SELECT * FROM pantry;


USE smart_pantry;
SHOW TABLES;
SELECT * FROM pantry;
 


SELECT *
FROM pantry
WHERE name LIKE '%eggs%'; 

USE smart_pantry;

SELECT name, quantity, unit
FROM pantry
WHERE name LIKE '%egg%';

UPDATE pantry
SET quantity = 3
WHERE LOWER(name) = LOWER('eggs')
LIMIT 1;

SELECT *
FROM pantry
WHERE name LIKE '%milk%';


-- lsof -t -i:5001 | xargs kill -9

SELECT *
FROM pantry


-- Total rows
SELECT COUNT(*) AS total_items FROM pantry;

-- Count by category
SELECT category, COUNT(*) AS count
FROM pantry
GROUP BY category
ORDER BY count DESC;

-- Full health summary
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN expiry_date < CURDATE() THEN 1 ELSE 0 END) AS expired,
    SUM(CASE WHEN expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) AS at_risk,
    SUM(CASE WHEN expiry_date > DATE_ADD(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) AS ok
FROM pantry;


-- Items EXPIRING TODAY (shows as AT RISK)
INSERT INTO pantry (name, category, quantity, unit, expiry_date) VALUES
('Baby Spinach',     'Produce',    1, 'bag',    '2026-04-28'),
('Greek Yogurt',     'Dairy',      2, 'cups',   '2026-04-28'),
('Fresh Salmon',     'Meat & Seafood', 1, 'fillet', '2026-04-28');

-- Items expiring in 1-2 days (shows as AT RISK)
INSERT INTO pantry (name, category, quantity, unit, expiry_date) VALUES
('Chicken Breast',   'Meat & Seafood', 2, 'lbs',   '2026-04-29'),
('Shredded Mozzarella', 'Dairy',    1, 'bag',   '2026-04-30'),
('Cherry Tomatoes',  'Produce',    1, 'pint',  '2026-04-30');

-- Items ALREADY EXPIRED (shows as EXPIRED)
INSERT INTO pantry (name, category, quantity, unit, expiry_date) VALUES
('Whole Wheat Bread','Bakery',     1, 'loaf',  '2026-04-24'),
('Cheddar Slices',   'Dairy',      1, 'pack',  '2026-04-22'),
('Leftover Rice',    'Dry Goods & Pasta', 1, 'cup', '2026-04-20'),
('Heavy Cream',      'Dairy',      1, 'cup',   '2026-04-25');
