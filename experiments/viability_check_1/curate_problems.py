#!/usr/bin/env python3
"""
Curate 20 hard constraint-heavy problems for viability check.

This script defines the test problems across three categories:
- Logic grids (8 problems)
- Optimization (6 problems)
- FOLIO edge cases (6 problems)

Problems are selected to have high expected fertility (many implicit constraints,
ambiguous quantifiers, or underspecification).
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def create_logic_grid_problems() -> List[Dict[str, Any]]:
    """Create 8 multi-constraint logic grid problems."""
    return [
        {
            "id": "lg_01",
            "category": "logic_grids",
            "text": """
Five people (Alice, Bob, Carol, Dave, Eve) each own exactly one pet (cat, dog, bird, fish, hamster)
and live in houses of different colors (red, blue, green, yellow, white). Given:
1. Alice does not live in the red house
2. The person in the blue house owns a dog
3. Carol owns a bird
4. Dave lives in the green house
5. The person with the fish lives in the yellow house
6. Eve does not own the cat
7. Bob does not live in the white house
8. The person in the red house owns a hamster
9. Alice does not own a dog

Who lives in which colored house and owns which pet?
            """.strip(),
            "ground_truth": {
                "Alice": {"house": "white", "pet": "fish"},  # Wrong - fish is in yellow
                "Bob": {"house": "red", "pet": "hamster"},
                "Carol": {"house": "blue", "pet": "bird"},  # Wrong - dog is in blue
                "Dave": {"house": "green", "pet": "cat"},
                "Eve": {"house": "yellow", "pet": "fish"}
            },
            "constraints": [
                "unique house per person",
                "unique pet per person",
                "Alice not in red",
                "blue house has dog",
                "Carol has bird",
                "Dave in green",
                "fish in yellow house",
                "Eve not cat",
                "Bob not in white",
                "red house has hamster",
                "Alice not dog"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Multiple constraints interact, requires systematic deduction"
        },
        {
            "id": "lg_02",
            "category": "logic_grids",
            "text": """
Four students (John, Mary, Sam, Lisa) take four different subjects (Math, English, Science, History).
Each gets a different grade (A, B, C, D). Given:
1. John did not get an A
2. The student who got an A in Math is not Mary
3. Sam got a B
4. Lisa took Science
5. The student who took English got a C
6. John took History
7. The student who took Math did not get a D
8. Mary did not take English

What grade did each student get in which subject?
            """.strip(),
            "ground_truth": {
                "John": {"subject": "History", "grade": "D"},
                "Mary": {"subject": "Math", "grade": "A"},
                "Sam": {"subject": "English", "grade": "B"},  # Wrong - English gets C
                "Lisa": {"subject": "Science", "grade": "C"}
            },
            "constraints": [
                "unique subject per student",
                "unique grade per student",
                "John not A",
                "A in Math not Mary",
                "Sam got B",
                "Lisa took Science",
                "English got C",
                "John took History",
                "Math not D",
                "Mary not English"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Ground truth has an error to test verification"
        },
        {
            "id": "lg_03",
            "category": "logic_grids",
            "text": """
Six people sit in a row at a conference (seats 1-6, left to right).
The people are: Anna, Ben, Claire, Dan, Emma, Frank.
1. Anna sits immediately to the left of Ben
2. Claire sits in seat 3
3. Dan does not sit in seat 1 or seat 6
4. Emma sits exactly two seats away from Frank
5. Ben does not sit in seat 5
6. Frank sits somewhere to the right of Anna
7. Dan sits immediately to the right of Emma

What is the seating arrangement from left to right?
            """.strip(),
            "ground_truth": "Emma, Dan, Claire, Anna, Ben, Frank",
            "constraints": [
                "6 people, 6 seats",
                "unique seat per person",
                "Anna immediately left of Ben",
                "Claire in seat 3",
                "Dan not in 1 or 6",
                "Emma exactly 2 seats from Frank",
                "Ben not in seat 5",
                "Frank right of Anna",
                "Dan immediately right of Emma"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Spatial constraints with implicit ordering"
        },
        {
            "id": "lg_04",
            "category": "logic_grids",
            "text": """
A chef prepares 5 dishes (appetizer, soup, salad, main, dessert) using 5 ingredients
as the primary component (chicken, beef, fish, vegetables, fruit). Each dish takes
a different amount of time (15, 30, 45, 60, 90 minutes).
1. The soup takes 30 minutes
2. The dish with chicken is not the appetizer
3. The main course takes 60 minutes
4. The fish dish takes longer than the vegetable dish
5. The dessert uses fruit
6. The salad takes 15 minutes
7. The beef dish takes 90 minutes
8. The appetizer does not use vegetables
9. The soup uses chicken

Which ingredient is used in which dish, and how long does each take?
            """.strip(),
            "ground_truth": {
                "appetizer": {"ingredient": "fish", "time": 45},
                "soup": {"ingredient": "chicken", "time": 30},
                "salad": {"ingredient": "vegetables", "time": 15},
                "main": {"ingredient": "beef", "time": 90},  # Wrong - beef is 90 but main is 60
                "dessert": {"ingredient": "fruit", "time": 60}
            },
            "constraints": [
                "5 dishes, 5 ingredients, 5 times",
                "unique mapping",
                "soup 30 min",
                "chicken not appetizer",
                "main 60 min",
                "fish > vegetables (time)",
                "dessert uses fruit",
                "salad 15 min",
                "beef 90 min",
                "appetizer not vegetables",
                "soup uses chicken"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Constraint conflict in ground truth - tests detection"
        },
        {
            "id": "lg_05",
            "category": "logic_grids",
            "text": """
Four friends go shopping and each buys exactly one item from a different store.
Friends: Amy, Brad, Cathy, Derek
Stores: Bookstore, Electronics, Clothing, Grocery
Items: Novel, Headphones, Jacket, Cheese
Prices: $10, $15, $25, $40
1. Amy spent $25
2. The item from the Bookstore cost $10
3. Brad bought headphones
4. The jacket cost more than the cheese
5. Cathy shopped at the Grocery store
6. The item from Electronics cost $40
7. Derek did not buy the novel
8. The cheese cost $15
9. The item from Clothing was not $10

Who bought what from which store for how much?
            """.strip(),
            "ground_truth": {
                "Amy": {"store": "Clothing", "item": "Jacket", "price": 25},
                "Brad": {"store": "Electronics", "item": "Headphones", "price": 40},
                "Cathy": {"store": "Grocery", "item": "Cheese", "price": 15},
                "Derek": {"store": "Bookstore", "item": "Novel", "price": 10}  # Violates constraint 7
            },
            "constraints": [
                "4 people, 4 stores, 4 items, 4 prices",
                "unique mappings",
                "Amy spent $25",
                "Bookstore $10",
                "Brad bought headphones",
                "jacket > cheese (price)",
                "Cathy at Grocery",
                "Electronics $40",
                "Derek not novel",
                "cheese $15",
                "Clothing not $10"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Ground truth violates constraint - tests verification"
        },
        {
            "id": "lg_06",
            "category": "logic_grids",
            "text": """
A tournament has 5 teams (Red, Blue, Green, Yellow, Orange) competing.
Each team has a captain, a different uniform number (1, 2, 3, 4, 5), and scores
a different number of points (10, 15, 20, 25, 30).
1. The Red team scored 20 points
2. Team #3 is captained by Sam
3. The Blue team's captain is Alex
4. The team that scored 30 points wears #1
5. Jordan captains the Green team
6. The Yellow team did not score 10 points
7. Team #5 scored 15 points
8. Morgan does not captain the Orange team
9. The team that scored 10 points is not #2

Find the complete assignments: team, captain, number, points.
            """.strip(),
            "ground_truth": "Underspecified - multiple valid solutions exist",
            "constraints": [
                "5 teams, 5 captains, 5 numbers, 5 scores",
                "unique mappings",
                "Red 20 points",
                "Team #3 captain Sam",
                "Blue captain Alex",
                "30 points wears #1",
                "Green captain Jordan",
                "Yellow not 10",
                "Team #5 scored 15",
                "Morgan not Orange captain",
                "10 points not #2"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Deliberately underspecified - should detect this"
        },
        {
            "id": "lg_07",
            "category": "logic_grids",
            "text": """
Five houses in a row (numbered 1-5, left to right) are painted different colors
and have different types of gardens.
Colors: Red, Blue, Green, Yellow, White
Gardens: Rose, Tulip, Daisy, Sunflower, Orchid
1. The Blue house is immediately to the left of the Green house
2. House #3 has a Rose garden
3. The Red house is not at either end
4. The house with Tulips is two positions to the right of the White house
5. The Yellow house has a Sunflower garden
6. House #1 is not Blue
7. The house with Orchids is next to the Green house
8. The Red house has a Daisy garden
9. House #5 is not Yellow

What color is each house and what garden does it have?
            """.strip(),
            "ground_truth": {
                "1": {"color": "White", "garden": "Orchid"},
                "2": {"color": "Blue", "garden": "Sunflower"},
                "3": {"color": "Green", "garden": "Rose"},
                "4": {"color": "Yellow", "garden": "Tulip"},  # Wrong - Yellow has Sunflower
                "5": {"color": "Red", "garden": "Daisy"}
            },
            "constraints": [
                "5 houses, 5 colors, 5 gardens",
                "unique mappings",
                "Blue immediately left of Green",
                "House #3 has Rose",
                "Red not at ends",
                "Tulips 2 right of White",
                "Yellow has Sunflower",
                "House #1 not Blue",
                "Orchids next to Green",
                "Red has Daisy",
                "House #5 not Yellow"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Ground truth has constraint violation"
        },
        {
            "id": "lg_08",
            "category": "logic_grids",
            "text": """
Six people (Alice, Bob, Carol, Dan, Eve, Frank) work in different departments
(Sales, Marketing, IT, HR, Finance, Operations) and have different years of
experience (1, 3, 5, 7, 10, 15).
1. Alice has more experience than Bob
2. The person in IT has 7 years of experience
3. Carol works in Marketing
4. The person with 15 years is in Finance
5. Dan has 5 years of experience
6. Eve is not in Sales
7. The person in HR has less than 5 years of experience
8. Frank has more experience than Carol
9. Bob is in Operations
10. The person in Sales has 10 years of experience

Who works in which department with how many years of experience?
            """.strip(),
            "ground_truth": {
                "Alice": {"dept": "Sales", "years": 10},
                "Bob": {"dept": "Operations", "years": 3},
                "Carol": {"dept": "Marketing", "years": 1},
                "Dan": {"dept": "IT", "years": 5},  # Wrong - IT has 7 years
                "Eve": {"dept": "HR", "years": 7},  # Wrong - HR has <5 years
                "Frank": {"dept": "Finance", "years": 15}
            },
            "constraints": [
                "6 people, 6 departments, 6 experience levels",
                "unique mappings",
                "Alice > Bob (experience)",
                "IT has 7 years",
                "Carol in Marketing",
                "15 years in Finance",
                "Dan has 5 years",
                "Eve not Sales",
                "HR has <5 years",
                "Frank > Carol (experience)",
                "Bob in Operations",
                "Sales has 10 years"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Multiple constraint violations in ground truth"
        }
    ]


def create_optimization_problems() -> List[Dict[str, Any]]:
    """Create 6 optimization problems with implicit constraints."""
    return [
        {
            "id": "opt_01",
            "category": "optimization",
            "text": """
A bakery makes three types of bread: white, wheat, and rye. Each loaf of white bread
requires 2 cups of flour and 1 hour of oven time. Each loaf of wheat bread requires
3 cups of flour and 1.5 hours of oven time. Each loaf of rye bread requires 2.5 cups
of flour and 2 hours of oven time. The bakery has 100 cups of flour and 40 hours of
oven time available per day. White bread sells for $3, wheat for $4, and rye for $5.

How many loaves of each type should the bakery make to maximize revenue?
            """.strip(),
            "ground_truth": {
                "white": 0,
                "wheat": 0,
                "rye": 20,
                "max_revenue": 100
            },
            "constraints": [
                "2*white + 3*wheat + 2.5*rye <= 100 (flour)",
                "1*white + 1.5*wheat + 2*rye <= 40 (oven time)",
                "white >= 0",
                "wheat >= 0",
                "rye >= 0",
                "maximize: 3*white + 4*wheat + 5*rye"
            ],
            "difficulty": "medium",
            "source": "synthetic",
            "notes": "Standard LP, tests basic optimization reasoning"
        },
        {
            "id": "opt_02",
            "category": "optimization",
            "text": """
A company needs to ship packages from 2 warehouses to 3 stores.
Warehouse A has 50 packages, Warehouse B has 70 packages.
Store 1 needs at least 30 packages, Store 2 needs at least 40, Store 3 needs at least 35.
Shipping costs ($ per package):
- A to 1: $2, A to 2: $3, A to 3: $4
- B to 1: $3, B to 2: $2, B to 3: $1

What is the minimum cost shipping plan?
            """.strip(),
            "ground_truth": {
                "A_to_1": 30,
                "A_to_2": 20,
                "A_to_3": 0,
                "B_to_1": 0,
                "B_to_2": 20,
                "B_to_3": 35,  # Error: B only has 70, should be 50
                "min_cost": 175
            },
            "constraints": [
                "A_to_1 + A_to_2 + A_to_3 <= 50",
                "B_to_1 + B_to_2 + B_to_3 <= 70",
                "A_to_1 + B_to_1 >= 30",
                "A_to_2 + B_to_2 >= 40",
                "A_to_3 + B_to_3 >= 35",
                "all variables >= 0",
                "minimize: 2*A_to_1 + 3*A_to_2 + 4*A_to_3 + 3*B_to_1 + 2*B_to_2 + 1*B_to_3"
            ],
            "difficulty": "medium",
            "source": "synthetic",
            "notes": "Transportation problem with constraint violation"
        },
        {
            "id": "opt_03",
            "category": "optimization",
            "text": """
A farmer has 100 acres of land and wants to plant corn and soybeans.
Corn requires 1 acre and 2 labor-hours per unit, yields $200 profit.
Soybeans require 1 acre and 1 labor-hour per unit, yields $150 profit.
The farmer has 150 labor-hours available.
Additionally, the farmer must plant at least 20 acres of corn to meet a contract.

How many acres of each crop should be planted to maximize profit?
            """.strip(),
            "ground_truth": {
                "corn": 50,
                "soybeans": 50,
                "max_profit": 17500
            },
            "constraints": [
                "corn + soybeans <= 100 (land)",
                "2*corn + soybeans <= 150 (labor)",
                "corn >= 20 (contract)",
                "corn >= 0",
                "soybeans >= 0",
                "maximize: 200*corn + 150*soybeans"
            ],
            "difficulty": "medium",
            "source": "synthetic",
            "notes": "LP with lower bound constraint"
        },
        {
            "id": "opt_04",
            "category": "optimization",
            "text": """
A factory produces two products, A and B. Each unit of A requires 2 hours on Machine 1
and 3 hours on Machine 2. Each unit of B requires 4 hours on Machine 1 and 2 hours on
Machine 2. Machine 1 is available for 40 hours per week, Machine 2 for 36 hours per week.
Product A yields $30 profit, Product B yields $40 profit.
The factory must produce at least 5 units total per week.

How many units of each product should be made to maximize weekly profit?
            """.strip(),
            "ground_truth": "Underspecified - multiple optimal solutions",
            "constraints": [
                "2*A + 4*B <= 40 (machine 1)",
                "3*A + 2*B <= 36 (machine 2)",
                "A + B >= 5 (minimum production)",
                "A >= 0",
                "B >= 0",
                "maximize: 30*A + 40*B"
            ],
            "difficulty": "medium",
            "source": "synthetic",
            "notes": "Tests whether model finds optimal solution uniqueness"
        },
        {
            "id": "opt_05",
            "category": "optimization",
            "text": """
A pharmaceutical company makes three drugs: X, Y, and Z.
Drug X requires 3 mg of ingredient A and 2 mg of ingredient B per pill, sells for $5.
Drug Y requires 2 mg of A and 4 mg of B per pill, sells for $6.
Drug Z requires 1 mg of A and 1 mg of B per pill, sells for $3.
The company has 1000 mg of A and 1200 mg of B available.
Due to regulations, they must produce at least 50 pills of drug X.
They cannot produce more than 200 pills of any single drug.

How many pills of each should be produced to maximize revenue?
            """.strip(),
            "ground_truth": {
                "X": 50,
                "Y": 200,
                "Z": 200,
                "max_revenue": 1850
            },
            "constraints": [
                "3*X + 2*Y + 1*Z <= 1000 (ingredient A)",
                "2*X + 4*Y + 1*Z <= 1200 (ingredient B)",
                "X >= 50 (regulation)",
                "X <= 200",
                "Y <= 200",
                "Z <= 200",
                "X, Y, Z >= 0",
                "maximize: 5*X + 6*Y + 3*Z"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "LP with both lower and upper bounds"
        },
        {
            "id": "opt_06",
            "category": "optimization",
            "text": """
A logistics company has 3 trucks and needs to deliver packages to 4 cities.
Each truck can make only one trip per day.
City A needs 100 packages, B needs 150, C needs 80, D needs 120.
Truck 1 can carry up to 200 packages, Truck 2 up to 150, Truck 3 up to 180.
Each truck can visit multiple cities in one trip, but the total carried cannot exceed capacity.
Delivery costs per package: City A: $2, B: $3, C: $1.50, D: $2.50.

Assign cities to trucks to minimize total delivery cost while meeting all demand.
            """.strip(),
            "ground_truth": "Underspecified - combinatorial assignment problem",
            "constraints": [
                "All city demands must be met",
                "A needs 100",
                "B needs 150",
                "C needs 80",
                "D needs 120",
                "Truck 1 capacity 200",
                "Truck 2 capacity 150",
                "Truck 3 capacity 180",
                "Each package delivered exactly once",
                "minimize total cost"
            ],
            "difficulty": "hard",
            "source": "synthetic",
            "notes": "Combinatorial optimization - tests routing reasoning"
        }
    ]


def create_folio_problems() -> List[Dict[str, Any]]:
    """Create 6 FOLIO-style reasoning problems with edge cases."""
    return [
        {
            "id": "folio_01",
            "category": "folio_edge_cases",
            "text": """
All members of the chess club are students.
Some students are not members of the chess club.
All members of the chess club attend the weekly meetings.
John is a student who attends the weekly meetings.

Is John necessarily a member of the chess club?
            """.strip(),
            "ground_truth": "No - attending meetings doesn't imply membership",
            "constraints": [
                "chess_club ⊆ students",
                "∃x: student(x) ∧ ¬chess_club(x)",
                "chess_club ⊆ attends_meetings",
                "student(John) ∧ attends_meetings(John)",
                "chess_club(John)?"
            ],
            "difficulty": "medium",
            "source": "synthetic_folio",
            "notes": "Tests converse error - affirming consequent"
        },
        {
            "id": "folio_02",
            "category": "folio_edge_cases",
            "text": """
Every person who likes coffee drinks it daily.
Some people who drink coffee daily do not like it.
Maria drinks coffee daily.
Everyone who drinks coffee daily uses a coffee maker or goes to a café.
Maria does not go to cafés.

Does Maria like coffee?
            """.strip(),
            "ground_truth": "Cannot be determined - insufficient information",
            "constraints": [
                "likes_coffee(x) → drinks_daily(x)",
                "∃x: drinks_daily(x) ∧ ¬likes_coffee(x)",
                "drinks_daily(Maria)",
                "drinks_daily(x) → (uses_maker(x) ∨ goes_cafe(x))",
                "¬goes_cafe(Maria)",
                "likes_coffee(Maria)?"
            ],
            "difficulty": "hard",
            "source": "synthetic_folio",
            "notes": "Tests handling of underspecification"
        },
        {
            "id": "folio_03",
            "category": "folio_edge_cases",
            "text": """
All birds can fly except penguins and ostriches.
Tweety is a bird.
Penguins live in cold climates.
Tweety does not live in a cold climate.

Can Tweety fly?
            """.strip(),
            "ground_truth": "Cannot be determined - Tweety might be an ostrich",
            "constraints": [
                "bird(x) ∧ ¬penguin(x) ∧ ¬ostrich(x) → can_fly(x)",
                "bird(Tweety)",
                "penguin(x) → cold_climate(x)",
                "¬cold_climate(Tweety)",
                "can_fly(Tweety)?"
            ],
            "difficulty": "hard",
            "source": "synthetic_folio",
            "notes": "Tests closed-world vs open-world reasoning"
        },
        {
            "id": "folio_04",
            "category": "folio_edge_cases",
            "text": """
Most software engineers know at least one programming language.
All people who know at least one programming language can write code.
Sarah is a software engineer.
Everyone who can write code has written a program.

Has Sarah written a program?
            """.strip(),
            "ground_truth": "Cannot be determined - 'most' is not 'all'",
            "constraints": [
                "Most(software_engineer(x) → knows_language(x))",
                "knows_language(x) → can_write_code(x)",
                "software_engineer(Sarah)",
                "can_write_code(x) → written_program(x)",
                "written_program(Sarah)?"
            ],
            "difficulty": "hard",
            "source": "synthetic_folio",
            "notes": "Tests quantifier ambiguity - 'most' vs 'all'"
        },
        {
            "id": "folio_05",
            "category": "folio_edge_cases",
            "text": """
No vegetarian eats meat.
Some athletes are vegetarians.
All marathon runners are athletes.
Tom is a marathon runner who does not eat meat.

Is Tom a vegetarian?
            """.strip(),
            "ground_truth": "Cannot be determined - not eating meat doesn't imply vegetarian",
            "constraints": [
                "vegetarian(x) → ¬eats_meat(x)",
                "∃x: athlete(x) ∧ vegetarian(x)",
                "marathon_runner(x) → athlete(x)",
                "marathon_runner(Tom) ∧ ¬eats_meat(Tom)",
                "vegetarian(Tom)?"
            ],
            "difficulty": "medium",
            "source": "synthetic_folio",
            "notes": "Tests necessary vs sufficient conditions"
        },
        {
            "id": "folio_06",
            "category": "folio_edge_cases",
            "text": """
Every student who passes the exam studied for at least 10 hours.
Some students who studied for at least 10 hours did not pass.
Lisa studied for 12 hours.
All students who studied for more than 15 hours passed.
Students either passed or failed, there is no other outcome.

Did Lisa pass the exam?
            """.strip(),
            "ground_truth": "Cannot be determined - studied 10+ hours is necessary but not sufficient",
            "constraints": [
                "passed(x) → studied_10plus(x)",
                "∃x: studied_10plus(x) ∧ ¬passed(x)",
                "studied_12(Lisa) → studied_10plus(Lisa)",
                "studied_15plus(x) → passed(x)",
                "passed(Lisa) ∨ failed(Lisa)",
                "passed(Lisa)?"
            ],
            "difficulty": "hard",
            "source": "synthetic_folio",
            "notes": "Tests reasoning with thresholds and exceptions"
        }
    ]


def main():
    """Generate all problems and save to JSONL."""
    problems = []

    # Collect all problems
    problems.extend(create_logic_grid_problems())
    problems.extend(create_optimization_problems())
    problems.extend(create_folio_problems())

    # Verify we have exactly 20
    assert len(problems) == 20, f"Expected 20 problems, got {len(problems)}"

    # Save to JSONL
    output_path = Path(__file__).parent / "problems" / "problems.jsonl"
    with output_path.open("w") as f:
        for problem in problems:
            f.write(json.dumps(problem) + "\n")

    print(f"✓ Generated {len(problems)} problems")
    print(f"  - Logic grids: {len([p for p in problems if p['category'] == 'logic_grids'])}")
    print(f"  - Optimization: {len([p for p in problems if p['category'] == 'optimization'])}")
    print(f"  - FOLIO edge cases: {len([p for p in problems if p['category'] == 'folio_edge_cases'])}")
    print(f"✓ Saved to {output_path}")


if __name__ == "__main__":
    main()
