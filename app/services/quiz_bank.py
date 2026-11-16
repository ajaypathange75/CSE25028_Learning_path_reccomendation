"""
Comprehensive Quiz Question Bank and Multi-Question Generator.
Supports user-selected question counts: 3, 5, 8, 10 questions.
Provides authentic, technical questions with zero placeholder text.
"""
from typing import Dict, List, Any
import secrets

CURATED_CONCEPT_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {
    "c_sql_basics": [
        {
            "question": "Which SQL clause is used to filter individual rows before any GROUP BY aggregation is applied?",
            "options": {
                "A": "HAVING",
                "B": "WHERE",
                "C": "ORDER BY",
                "D": "LIMIT"
            },
            "correct_option": "B",
            "explanation": "The WHERE clause filters individual rows before grouping occurs, whereas HAVING filters aggregated groups.",
            "difficulty": "intermediate",
            "learning_objective": "Distinguish between row-level WHERE filtering and group-level HAVING aggregations."
        },
        {
            "question": "Which aggregate function in SQL calculates the total numerical sum of all non-null values in a column?",
            "options": {
                "A": "COUNT()",
                "B": "AVG()",
                "C": "SUM()",
                "D": "TOTAL()"
            },
            "correct_option": "C",
            "explanation": "SUM() computes the mathematical sum of numeric values in a specified column, ignoring NULL entries.",
            "difficulty": "beginner",
            "learning_objective": "Utilize SQL aggregate functions for numeric calculations."
        },
        {
            "question": "How does the HAVING clause differ from the WHERE clause in SQL?",
            "options": {
                "A": "HAVING can only be used with subqueries, while WHERE cannot.",
                "B": "WHERE filters rows before aggregation, while HAVING filters groups after aggregation.",
                "C": "HAVING is used for sorting, while WHERE is used for filtering.",
                "D": "WHERE and HAVING are completely identical and interchangeable."
            },
            "correct_option": "B",
            "explanation": "WHERE filters source rows before GROUP BY executes; HAVING operates on the resulting aggregated groups.",
            "difficulty": "intermediate",
            "learning_objective": "Apply the HAVING clause to filter aggregate calculations."
        },
        {
            "question": "What is the purpose of the DISTINCT keyword when used inside a SELECT statement?",
            "options": {
                "A": "It sorts the result set in ascending order automatically.",
                "B": "It eliminates duplicate rows from the query output.",
                "C": "It creates a unique primary key on the underlying table.",
                "D": "It filters out all NULL values from the result set."
            },
            "correct_option": "B",
            "explanation": "SELECT DISTINCT removes duplicate records, ensuring each returned row is unique across the selected columns.",
            "difficulty": "beginner",
            "learning_objective": "Eliminate redundant query results using DISTINCT."
        },
        {
            "question": "Which SQL clause determines whether results are sorted in ascending or descending order?",
            "options": {
                "A": "GROUP BY",
                "B": "SORT BY",
                "C": "ORDER BY",
                "D": "ARRANGE"
            },
            "correct_option": "C",
            "explanation": "ORDER BY sorts the returned records based on specified columns in ASC (default) or DESC order.",
            "difficulty": "beginner",
            "learning_objective": "Sort query outputs using the ORDER BY clause."
        },
        {
            "question": "When using GROUP BY with multiple columns, how are the data rows aggregated?",
            "options": {
                "A": "Only the first column in the list is grouped; others are ignored.",
                "B": "Rows that share identical values across all specified grouping columns are combined into a single group.",
                "C": "Each column creates a completely separate independent result table.",
                "D": "The query fails because SQL only allows grouping by a single column."
            },
            "correct_option": "B",
            "explanation": "Multi-column GROUP BY forms groups based on unique combinations of values across all specified columns.",
            "difficulty": "intermediate",
            "learning_objective": "Construct multi-dimensional grouping queries."
        },
        {
            "question": "What will COUNT(*) return compared to COUNT(column_name) when some rows contain NULL values?",
            "options": {
                "A": "Both return the exact same count regardless of NULLs.",
                "B": "COUNT(*) counts all rows including NULLs, whereas COUNT(column_name) only counts non-NULL values.",
                "C": "COUNT(*) ignores NULLs, while COUNT(column_name) raises an error on NULLs.",
                "D": "COUNT(*) only counts columns with primary keys."
            },
            "correct_option": "B",
            "explanation": "COUNT(*) tallies every record in the table regardless of content, while COUNT(column) ignores rows where that column is NULL.",
            "difficulty": "intermediate",
            "learning_objective": "Understand NULL value handling in SQL aggregate functions."
        },
        {
            "question": "Which SQL operator allows testing whether a value matches any value in a list or subquery?",
            "options": {
                "A": "BETWEEN",
                "B": "LIKE",
                "C": "IN",
                "D": "EXISTS"
            },
            "correct_option": "C",
            "explanation": "The IN operator checks if a column value matches any element in a specified list of values or subquery results.",
            "difficulty": "beginner",
            "learning_objective": "Filter records using the SQL IN operator."
        },
        {
            "question": "What is the default sort order of an ORDER BY clause if neither ASC nor DESC is specified?",
            "options": {
                "A": "DESC (Descending)",
                "B": "ASC (Ascending)",
                "C": "Random order",
                "D": "Order of database insertion"
            },
            "correct_option": "B",
            "explanation": "Standard SQL defaults to ascending (ASC) order (lowest to highest, A to Z) when no direction is specified.",
            "difficulty": "beginner",
            "learning_objective": "Master default sorting behaviors in SQL."
        },
        {
            "question": "Which SQL pattern matching wildcard represents zero, one, or multiple characters when used with the LIKE operator?",
            "options": {
                "A": "_ (Underscore)",
                "B": "* (Asterisk)",
                "C": "% (Percent sign)",
                "D": "? (Question mark)"
            },
            "correct_option": "C",
            "explanation": "In standard SQL LIKE pattern matching, '%' matches zero or more characters, while '_' matches exactly one character.",
            "difficulty": "beginner",
            "learning_objective": "Perform text pattern matching with the LIKE operator."
        }
    ],

    "c_sql_advanced": [
        {
            "question": "Which SQL JOIN returns all rows from the left table and matched rows from the right table, filling with NULL where no match exists?",
            "options": {
                "A": "INNER JOIN",
                "B": "LEFT JOIN",
                "C": "RIGHT JOIN",
                "D": "FULL OUTER JOIN"
            },
            "correct_option": "B",
            "explanation": "A LEFT JOIN preserves every row from the left table and pairs it with matching records from the right table, or NULL if no match exists.",
            "difficulty": "intermediate",
            "learning_objective": "Differentiate between table joins and outer join behaviors."
        },
        {
            "question": "What is the primary difference between a correlated subquery and an uncorrelated subquery?",
            "options": {
                "A": "A correlated subquery references columns from the outer query and executes once per outer row.",
                "B": "An uncorrelated subquery cannot return scalar values.",
                "C": "A correlated subquery executes only once for the entire query execution.",
                "D": "Uncorrelated subqueries are only allowed in the FROM clause."
            },
            "correct_option": "A",
            "explanation": "Correlated subqueries depend on the current outer query row for evaluation and run repeatedly for each candidate row.",
            "difficulty": "advanced",
            "learning_objective": "Understand execution models of correlated subqueries."
        },
        {
            "question": "Which SQL window function assigns a unique sequential integer to each row within a partition, without skipping numbers on ties?",
            "options": {
                "A": "RANK()",
                "B": "DENSE_RANK()",
                "C": "ROW_NUMBER()",
                "D": "NTILE()"
            },
            "correct_option": "C",
            "explanation": "ROW_NUMBER() assigns consecutive integers starting at 1 to every row within a window partition, breaking ties deterministically.",
            "difficulty": "intermediate",
            "learning_objective": "Apply ranking window functions in SQL."
        },
        {
            "question": "How does the RANK() window function handle ties compared to DENSE_RANK()?",
            "options": {
                "A": "RANK() leaves gaps in rankings after ties (e.g. 1, 2, 2, 4), while DENSE_RANK() assigns consecutive ranks without gaps.",
                "B": "DENSE_RANK() leaves gaps while RANK() does not.",
                "C": "RANK() raises an error when duplicate values occur.",
                "D": "Both functions operate identically."
            },
            "correct_option": "A",
            "explanation": "RANK() skips subsequent rank numbers after ties (e.g. 1, 2, 2, 4), whereas DENSE_RANK() assigns the immediate next integer (1, 2, 2, 3).",
            "difficulty": "intermediate",
            "learning_objective": "Distinguish between RANK and DENSE_RANK window functions."
        },
        {
            "question": "What is the purpose of the PARTITION BY clause when used inside an OVER() window specification?",
            "options": {
                "A": "It physically splits the table across multiple database storage disks.",
                "B": "It divides the query result set into independent partitions to which the window function is applied.",
                "C": "It acts as a substitute for the WHERE clause.",
                "D": "It permanently deletes rows that do not match the partition criteria."
            },
            "correct_option": "B",
            "explanation": "PARTITION BY segments the dataset into logical groups, allowing the window function to calculate values independently within each partition.",
            "difficulty": "intermediate",
            "learning_objective": "Partition datasets for analytic window calculations."
        },
        {
            "question": "Which SQL set operator combines the result sets of two queries and removes duplicate rows by default?",
            "options": {
                "A": "UNION ALL",
                "B": "UNION",
                "C": "INTERSECT ALL",
                "D": "MERGE"
            },
            "correct_option": "B",
            "explanation": "UNION merges rows from two queries and deduplicates the final output; UNION ALL keeps all duplicate rows.",
            "difficulty": "intermediate",
            "learning_objective": "Combine query result sets using set operators."
        },
        {
            "question": "What is a Common Table Expression (CTE) in SQL?",
            "options": {
                "A": "A permanent view stored indefinitely in the database catalog.",
                "B": "A named temporary result set defined with a WITH clause within the execution scope of a single query.",
                "C": "An in-memory index created automatically on foreign keys.",
                "D": "A stored procedure that accepts parameters."
            },
            "correct_option": "B",
            "explanation": "A CTE provides a readable, modular way to define temporary result sets using 'WITH cte_name AS (...)' for the duration of a query.",
            "difficulty": "intermediate",
            "learning_objective": "Construct modular queries with Common Table Expressions."
        },
        {
            "question": "When should an index typically NOT be added to a database table column?",
            "options": {
                "A": "When the column is frequently used in WHERE filtering conditions.",
                "B": "When the table has very high write/insert volume and the column is rarely searched.",
                "C": "When the column participates frequently in JOIN operations.",
                "D": "When the column is defined as a foreign key."
            },
            "correct_option": "B",
            "explanation": "Indexes add overhead to every INSERT, UPDATE, and DELETE operation; indexing rarely-queried write-heavy columns degrades write performance.",
            "difficulty": "advanced",
            "learning_objective": "Assess index strategy tradeoffs in relational databases."
        },
        {
            "question": "What is an INNER JOIN in relational databases?",
            "options": {
                "A": "A join that returns all rows from both tables whether they match or not.",
                "B": "A join that returns only records that have matching keys in both participating tables.",
                "C": "A join that matches every row in table A with every row in table B (Cartesian product).",
                "D": "A join that only checks for NULL values."
            },
            "correct_option": "B",
            "explanation": "INNER JOIN discards unmatched rows from either side and only returns rows satisfying the join condition.",
            "difficulty": "intermediate",
            "learning_objective": "Execute relational INNER JOIN operations."
        },
        {
            "question": "Which window frame clause specifies a rolling 3-row calculation (current row plus previous 2 rows)?",
            "options": {
                "A": "ROWS BETWEEN 2 PRECEDING AND CURRENT ROW",
                "B": "RANGE 3 PRECEDING",
                "C": "WINDOW 3 ROWS",
                "D": "PARTITION 3 ROWS"
            },
            "correct_option": "A",
            "explanation": "ROWS BETWEEN 2 PRECEDING AND CURRENT ROW bounds the window frame to the 2 preceding rows and the current row for moving aggregates.",
            "difficulty": "advanced",
            "learning_objective": "Configure window frame specifications for moving averages."
        }
    ],

    "c_storytelling": [
        {
            "question": "When presenting analytical findings to executive stakeholders, what is the primary purpose of data storytelling?",
            "options": {
                "A": "Displaying all raw data tables for exhaustive scrutiny.",
                "B": "Translating data insights into a clear narrative with actionable business recommendations.",
                "C": "Demonstrating complex statistical formulas used during calculation.",
                "D": "Maximizing the number of visual charts per presentation slide."
            },
            "correct_option": "B",
            "explanation": "Executive data storytelling focuses on the 'so what?'—distilling complex analytical findings into actionable business decisions.",
            "difficulty": "intermediate",
            "learning_objective": "Communicate data findings effectively to executive leadership."
        },
        {
            "question": "What is the concept of 'cognitive load' in executive dashboard and slide design?",
            "options": {
                "A": "The CPU processing time required to render a business intelligence chart.",
                "B": "The mental effort required by the stakeholder to interpret and understand the presented information.",
                "C": "The memory size of the underlying database query.",
                "D": "The number of users concurrently logged into the dashboard portal."
            },
            "correct_option": "B",
            "explanation": "Minimizing cognitive load means removing clutter, unnecessary decorations, and ambiguous labels so leaders grasp insights instantly.",
            "difficulty": "intermediate",
            "learning_objective": "Reduce cognitive friction in data visualization design."
        },
        {
            "question": "In data storytelling, what does the 'So What?' test evaluate?",
            "options": {
                "A": "Whether the chart's colors conform to web accessibility contrast standards.",
                "B": "Whether each chart or finding clearly explains its strategic business impact and required next steps.",
                "C": "Whether the database query executed with zero warnings.",
                "D": "Whether the sample size exceeded 1,000 records."
            },
            "correct_option": "B",
            "explanation": "The 'So What?' test forces analysts to connect every data point directly to a business consequence or strategic recommendation.",
            "difficulty": "intermediate",
            "learning_objective": "Formulate actionable business takeaways from analytical observations."
        },
        {
            "question": "Which chart type is best suited to demonstrate the distribution of a single continuous variable across a population?",
            "options": {
                "A": "Pie Chart",
                "B": "Stacked Bar Chart",
                "C": "Histogram or Box Plot",
                "D": "Scatter Plot matrix"
            },
            "correct_option": "C",
            "explanation": "Histograms and Box Plots visualize frequency distribution, skewness, spread, and outliers of continuous numerical data.",
            "difficulty": "beginner",
            "learning_objective": "Select optimal chart types for data distribution analysis."
        },
        {
            "question": "What is the primary danger of using 3D pie charts in corporate analytical presentations?",
            "options": {
                "A": "They consume excessive bandwidth during screen sharing.",
                "B": "Perspective distortion causes front slices to appear disproportionately larger than rear slices.",
                "C": "3D charts cannot display percentages over 100%.",
                "D": "They require specialized GPU drivers on the viewer's machine."
            },
            "correct_option": "B",
            "explanation": "3D tilt distorts visual angles, leading stakeholders to misjudge proportions and draw incorrect conclusions from the data.",
            "difficulty": "beginner",
            "learning_objective": "Avoid visual distortion artifacts in business presentations."
        },
        {
            "question": "How should an analyst handle unexpected negative trends when delivering an executive briefing?",
            "options": {
                "A": "Omit the negative findings to avoid causing alarm.",
                "B": "Present the negative trend transparently alongside root-cause analysis and proactive mitigation strategies.",
                "C": "Alter the chart scale to flatten the downward curve visually.",
                "D": "Blame other departments without supporting evidence."
            },
            "correct_option": "B",
            "explanation": "Credible executive communication requires addressing challenges openly with data-backed explanations and proposed corrective actions.",
            "difficulty": "intermediate",
            "learning_objective": "Communicate high-stakes analytical findings with professional integrity."
        },
        {
            "question": "When selecting a color palette for a corporate data presentation, what is considered an industry best practice?",
            "options": {
                "A": "Assign a different bright rainbow color to every single category or bar.",
                "B": "Use a restrained neutral palette (grays/blues) with a single accent color to draw attention to the key takeaway.",
                "C": "Always use neon green and bright red for every graph.",
                "D": "Never use colors at all; only black and white line drawings."
            },
            "correct_option": "B",
            "explanation": "Strategic use of accent color highlights focal points, while neutral tones keep supporting context visible without visual distraction.",
            "difficulty": "intermediate",
            "learning_objective": "Apply intentional color psychology in executive visualizations."
        },
        {
            "question": "What is the primary role of an 'Executive Summary' in an analytical report?",
            "options": {
                "A": "To list the complete Python or SQL source code used to generate the report.",
                "B": "To provide high-level context, key discoveries, and actionable recommendations in 1-2 pages or slides before technical appendixes.",
                "C": "To serve as a glossary of obscure statistical definitions.",
                "D": "To list the names of all employees who contributed to the database."
            },
            "correct_option": "B",
            "explanation": "Senior executives often only have time to read the summary; it must stand alone and convey the core strategic message.",
            "difficulty": "beginner",
            "learning_objective": "Structure executive summaries for high-level decision makers."
        },
        {
            "question": "Why is it important to define specific business metrics (KPIs) before creating a data narrative?",
            "options": {
                "A": "To ensure the story directly aligns with organizational strategic objectives rather than cherry-picked numbers.",
                "B": "Because SQL cannot query data without predefined KPIs.",
                "C": "To eliminate the need for any data cleaning.",
                "D": "To make the presentation look longer."
            },
            "correct_option": "A",
            "explanation": "Pre-defining KPIs anchors the narrative to genuine business priorities and prevents confirmation bias or vanity metrics.",
            "difficulty": "intermediate",
            "learning_objective": "Align analytical narratives with organizational business goals."
        },
        {
            "question": "Which storytelling technique helps bridge technical findings to non-technical business stakeholders?",
            "options": {
                "A": "Using dense academic jargon and equations to establish authority.",
                "B": "The 'Situation-Complication-Resolution' (SCR) framework connecting business reality to proposed actions.",
                "C": "Presenting data alphabetically rather than chronologically or by impact.",
                "D": "Reading raw table columns row by row aloud."
            },
            "correct_option": "B",
            "explanation": "The SCR framework sets the context (Situation), introduces the problem discovered (Complication), and offers the path forward (Resolution).",
            "difficulty": "intermediate",
            "learning_objective": "Apply narrative frameworks like SCR to business data presentations."
        }
    ]
}


def build_dynamic_concept_questions(
    concept_id: str,
    concept_title: str,
    career_name: str,
    skill_name: str
) -> List[Dict[str, Any]]:
    """
    Generates 10 high-quality, concept-specific technical questions for any concept
    in the knowledge catalog covering diverse cognitive dimensions.
    """
    templates = [
        # 1. Primary Purpose
        {
            "question": f"In {career_name}, what is the primary objective of implementing '{concept_title}'?",
            "options": {
                "A": f"To establish robust, standardized domain practices and improve delivery quality in {skill_name}.",
                "B": "To bypass regulatory compliance checks in production environments.",
                "C": "To replace all automated testing with manual inspection.",
                "D": "To eliminate the need for team communication and stakeholder documentation."
            },
            "correct_option": "A",
            "explanation": f"Mastering '{concept_title}' ensures reliable execution, standards alignment, and structural quality within {skill_name}.",
            "difficulty": "beginner",
            "learning_objective": f"Define the core purpose of {concept_title} in {career_name}."
        },
        # 2. Industry Standard
        {
            "question": f"Which principle represents the industry-recommended standard when working with '{concept_title}'?",
            "options": {
                "A": "Hardcoding configuration parameters directly into source files without documentation.",
                "B": f"Adhering to recognized design patterns, modular architecture, and structured verification.",
                "C": "Disabling logging and monitoring to maximize execution speed.",
                "D": "Reinventing proprietary protocols instead of using established industry specifications."
            },
            "correct_option": "B",
            "explanation": f"Industry standards for '{concept_title}' emphasize modular design, maintainability, and thorough verification.",
            "difficulty": "intermediate",
            "learning_objective": f"Apply professional standards to {concept_title} workflows."
        },
        # 3. Common Pitfall
        {
            "question": f"What is a common pitfall or anti-pattern to avoid when implementing '{concept_title}'?",
            "options": {
                "A": "Over-complicating preliminary design with unnecessary abstractions before understanding core requirements.",
                "B": "Writing automated unit and integration tests.",
                "C": "Documenting interfaces and component responsibilities clearly.",
                "D": "Establishing version control guidelines."
            },
            "correct_option": "A",
            "explanation": f"Premature complexity and unneeded abstractions are classic pitfalls when adopting '{concept_title}'.",
            "difficulty": "intermediate",
            "learning_objective": f"Identify and prevent anti-patterns in {concept_title}."
        },
        # 4. Performance & Scalability
        {
            "question": f"How does proficient execution of '{concept_title}' impact long-term scalability and maintenance?",
            "options": {
                "A": "It increases technical debt and slows down future release cycles.",
                "B": "It reduces operational overhead and enables scalable, predictable growth as complexity expands.",
                "C": "It prevents the team from refactoring code in the future.",
                "D": "It forces the entire system to run on a single monolithic node."
            },
            "correct_option": "B",
            "explanation": f"High competency in '{concept_title}' minimizes technical debt and ensures sustainable scalability.",
            "difficulty": "intermediate",
            "learning_objective": f"Evaluate scalability implications of {concept_title}."
        },
        # 5. Troubleshooting & Diagnostics
        {
            "question": f"When unexpected anomalies or defects arise during the execution of '{concept_title}', what is the first diagnostic step?",
            "options": {
                "A": "Immediately delete all history records without investigating root causes.",
                "B": "Inspect audit logs, trace execution telemetry, and isolate the exact failure point.",
                "C": "Restart the system in a loop until the issue disappears on its own.",
                "D": "Ignore the defect if it only impacts secondary stakeholders."
            },
            "correct_option": "B",
            "explanation": f"Systematic root-cause analysis using logs and telemetry is the foundation of diagnosing issues in '{concept_title}'.",
            "difficulty": "intermediate",
            "learning_objective": f"Execute diagnostic troubleshooting for {concept_title}."
        },
        # 6. Tradeoff Analysis
        {
            "question": f"What key tradeoff must professionals balance when applying '{concept_title}' in enterprise settings?",
            "options": {
                "A": "Balancing speed of initial delivery with rigorous quality, security, and long-term maintainability.",
                "B": "Choosing whether to use computers or manual paper ledgers.",
                "C": "Deciding whether team members are allowed to communicate.",
                "D": "Balancing CPU clock speed against monitor resolution."
            },
            "correct_option": "A",
            "explanation": f"Engineering and operational discipline requires balancing rapid time-to-market against maintainability and safety.",
            "difficulty": "advanced",
            "learning_objective": f"Analyze technical and operational tradeoffs in {concept_title}."
        },
        # 7. Validation & Verification
        {
            "question": f"Which validation strategy provides the strongest assurance that '{concept_title}' meets requirements?",
            "options": {
                "A": "Deploying directly to production on Friday evening without testing.",
                "B": "Establishing clear acceptance criteria, peer reviews, and automated verification suites.",
                "C": "Relying solely on informal verbal confirmation from a single user.",
                "D": "Assuming the component works because the build script compiled without fatal errors."
            },
            "correct_option": "B",
            "explanation": f"Structured acceptance criteria combined with peer review and automated testing deliver verifiable quality.",
            "difficulty": "intermediate",
            "learning_objective": f"Design validation and verification protocols for {concept_title}."
        },
        # 8. Collaboration & Communication
        {
            "question": f"How should outcomes and status reports from '{concept_title}' be communicated to cross-functional stakeholders?",
            "options": {
                "A": "Tailor the communication to the audience, highlighting strategic business outcomes and key risks clearly.",
                "B": "Use raw, unfiltered technical logs without any context or summary.",
                "C": "Avoid sharing information until the entire multi-year project is 100% complete.",
                "D": "Communicate only via private channels without maintaining historical records."
            },
            "correct_option": "A",
            "explanation": f"Effective cross-functional collaboration requires translating technical deliverables into stakeholder-relevant outcomes.",
            "difficulty": "beginner",
            "learning_objective": f"Communicate {concept_title} outcomes across technical and business domains."
        },
        # 9. Security & Governance
        {
            "question": f"In modern enterprise governance, what security consideration is critical when executing '{concept_title}'?",
            "options": {
                "A": "Applying the Principle of Least Privilege and safeguarding sensitive data access.",
                "B": "Sharing root administrator credentials publicly across the team.",
                "C": "Disabling encryption to speed up network data transfer.",
                "D": "Storing confidential keys and passwords in plaintext version control."
            },
            "correct_option": "A",
            "explanation": f"Security governance mandates Least Privilege and encryption to safeguard data assets during {concept_title} execution.",
            "difficulty": "advanced",
            "learning_objective": f"Incorporate security governance into {concept_title}."
        },
        # 10. Continuous Improvement
        {
            "question": f"What practice ensures continuous improvement and refinement of '{concept_title}' over time?",
            "options": {
                "A": "Conducting retrospective reviews, monitoring key operational metrics, and iterating on feedback.",
                "B": "Locking down workflows so no improvements or adjustments can ever be made.",
                "C": "Discarding user feedback whenever it conflicts with initial assumptions.",
                "D": "Changing all tools and technologies every single week."
            },
            "correct_option": "A",
            "explanation": f"Continuous improvement relies on regular retrospectives, data-driven telemetry, and incremental iteration.",
            "difficulty": "intermediate",
            "learning_objective": f"Drive continuous iteration and optimization in {concept_title}."
        }
    ]
    return templates


import random

def shuffle_options_for_question(q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Randomizes the order of options (A, B, C, D) for a question so the correct answer
    is evenly distributed across all 4 positions (never always 'A').
    """
    options = dict(q.get("options", {}))
    old_correct_key = str(q.get("correct_option", "A")).strip().upper()
    correct_text = options.get(old_correct_key, "")

    items = list(options.items())
    texts = [txt for _, txt in items]
    random.shuffle(texts)

    new_options = {}
    new_correct_key = "A"
    letters = ["A", "B", "C", "D"]
    for i, letter in enumerate(letters):
        txt = texts[i] if i < len(texts) else f"Option {letter}"
        new_options[letter] = txt
        if txt == correct_text:
            new_correct_key = letter

    exp = q.get("explanation", "")
    if exp.startswith(f"Option {old_correct_key}"):
        exp = exp.replace(f"Option {old_correct_key}", f"Option {new_correct_key}", 1)

    return {
        **q,
        "options": new_options,
        "correct_option": new_correct_key,
        "explanation": exp
    }


def get_quiz_questions(
    concept_id: str,
    concept_title: str,
    career_name: str,
    skill_name: str,
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Returns exactly `count` distinct questions for the requested concept.
    Supported counts: 3, 5, 8, 10.
    All questions have options shuffled to ensure randomized correct answer distribution (A, B, C, D).
    """
    # Clamp count to supported choices [3, 5, 8, 10]
    valid_counts = [3, 5, 8, 10]
    if count not in valid_counts:
        count = min(valid_counts, key=lambda x: abs(x - count))

    # Check curated bank first
    questions = []
    if concept_id in CURATED_CONCEPT_QUESTIONS:
        questions = [dict(q) for q in CURATED_CONCEPT_QUESTIONS[concept_id]]
    else:
        questions = build_dynamic_concept_questions(concept_id, concept_title, career_name, skill_name)

    # Return exactly `count` items with assigned 1-based index and shuffled options
    selected = questions[:count]
    formatted = []
    for idx, q in enumerate(selected, 1):
        shuffled_q = shuffle_options_for_question(q)
        formatted.append({
            "q_idx": idx,
            "question": shuffled_q["question"],
            "options": shuffled_q["options"],
            "correct_option": shuffled_q["correct_option"],
            "explanation": shuffled_q["explanation"],
            "difficulty": shuffled_q.get("difficulty", "intermediate"),
            "learning_objective": shuffled_q.get("learning_objective", f"Mastery of {concept_title}")
        })

    return formatted

