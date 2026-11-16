from typing import Dict, List, Set, Optional, Any
from collections import defaultdict, deque

class CareerKnowledgeGraph:
    """
    In-memory, maintainable Career Knowledge Graph representing:
    - Careers
    - Skills
    - Concepts
    - Courses & Resources
    - Projects
    - Explicit Prerequisites & Relationships
    """
    def __init__(self):
        # Nodes
        self.careers: Dict[str, Dict[str, Any]] = {}
        self.skills: Dict[str, Dict[str, Any]] = {}
        self.concepts: Dict[str, Dict[str, Any]] = {}
        self.courses: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.projects: Dict[str, Dict[str, Any]] = {}

        # Edges / Explicit Relationships
        self.career_skills: Dict[str, List[str]] = defaultdict(list)          # Career -> [Skill]
        self.skill_concepts: Dict[str, List[str]] = defaultdict(list)        # Skill -> [Concept]
        self.concept_prerequisites: Dict[str, List[str]] = defaultdict(list) # Concept -> [Prerequisite Concepts]
        self.course_concepts: Dict[str, List[str]] = defaultdict(list)       # Course -> [Concept]
        self.resource_concepts: Dict[str, List[str]] = defaultdict(list)     # Resource -> [Concept]
        self.project_skills: Dict[str, List[str]] = defaultdict(list)        # Project -> [Skill]
        self.project_concepts: Dict[str, List[str]] = defaultdict(list)      # Project -> [Concept]

        self._initialize_graph()

    def _initialize_graph(self):
        """Constructs the comprehensive career domain knowledge graph."""
        # 1. Careers Catalog with metadata
        career_catalog = {
            "Software Engineer": {
                "overview": "Designs, builds, and maintains robust software systems, architectures, and applications.",
                "learning_objectives": [
                    "Master core algorithms and data structures",
                    "Build scalable backend services and APIs",
                    "Apply clean architecture and unit testing principles"
                ],
                "career_requirements": [
                    "Proficiency in at least one modern language (Python, Java, Go, C++)",
                    "Solid understanding of relational and NoSQL databases",
                    "Experience with version control (Git) and CI/CD pipelines"
                ]
            },
            "Data Analyst": {
                "overview": "Inspects, cleans, transforms, and models data to discover actionable insights and support strategic decisions.",
                "learning_objectives": [
                    "Execute complex SQL queries for multi-table data aggregation",
                    "Conduct exploratory data analysis and statistical validation",
                    "Design executive BI dashboards with Tableau or Power BI"
                ],
                "career_requirements": [
                    "Proficiency in SQL and Python/R data libraries (Pandas, NumPy)",
                    "Expertise in dashboard creation and data storytelling",
                    "Understanding of business metrics and hypothesis testing"
                ]
            },
            "Web Developer": {
                "overview": "Creates engaging, performant web applications spanning responsive frontends and resilient backends.",
                "learning_objectives": [
                    "Build dynamic, mobile-friendly interfaces with modern HTML/CSS/JavaScript",
                    "Architect RESTful APIs and integrate third-party web services",
                    "Implement web security, authentication, and cloud deployment"
                ],
                "career_requirements": [
                    "Modern frontend frameworks (React, Vue) and CSS layout systems",
                    "Server-side scripting (Node.js, FastAPI, Django)",
                    "HTTP protocols, caching, and responsive design principles"
                ]
            },
            "Business Analyst": {
                "overview": "Bridges business stakeholders and technical teams by eliciting requirements and analyzing processes.",
                "learning_objectives": [
                    "Develop clear Business Requirements Documents (BRD) and user stories",
                    "Model operational workflows using BPMN 2.0 standard notation",
                    "Analyze cost-benefit trade-offs with financial metrics"
                ],
                "career_requirements": [
                    "Requirement elicitation and stakeholder interviewing",
                    "Agile/Scrum familiarity and backlog grooming",
                    "Process modeling and data-backed business reporting"
                ]
            },
            "Project Manager": {
                "overview": "Leads cross-functional initiatives from inception to delivery, balancing scope, schedule, and resources.",
                "learning_objectives": [
                    "Define Work Breakdown Structures (WBS) and milestone roadmaps",
                    "Facilitate sprint cadences, standups, and retrospective reviews",
                    "Proactively identify risks and execute mitigation strategies"
                ],
                "career_requirements": [
                    "Proficiency in Jira, Asana, or MS Project",
                    "PMP / Agile Certified Practitioner knowledge",
                    "High-impact stakeholder communication and resource leveling"
                ]
            },
            "Graphic Designer": {
                "overview": "Communicates ideas visually through typography, imagery, color palettes, and digital layout.",
                "learning_objectives": [
                    "Apply color harmony, visual hierarchy, and grid systems",
                    "Create vector assets and high-fidelity mockups in Figma and Illustrator",
                    "Establish comprehensive brand style guidelines"
                ],
                "career_requirements": [
                    "Strong portfolio showcasing branding and digital illustration",
                    "Mastery of Figma, Adobe Creative Cloud (Illustrator, Photoshop)",
                    "Deep understanding of responsive design and visual composition"
                ]
            },
            "HR Manager": {
                "overview": "Oversees talent acquisition, employee relations, compliance, culture, and organizational growth.",
                "learning_objectives": [
                    "Build structured recruiting pipelines and competency rubrics",
                    "Navigate labor compliance, ethics, and dispute resolution",
                    "Formulate performance review cycles and retention programs"
                ],
                "career_requirements": [
                    "Knowledge of labor regulations and HR Information Systems (HRIS)",
                    "Empathetic conflict resolution and negotiation skills",
                    "Strategic workforce planning and corporate culture building"
                ]
            },
            "Marketing Specialist": {
                "overview": "Plans and executes multi-channel campaigns to generate brand awareness, leads, and customer retention.",
                "learning_objectives": [
                    "Formulate data-driven customer acquisition funnels",
                    "Implement SEO best practices and content marketing clusters",
                    "Optimize paid ad campaigns (Google Ads, Meta) through A/B testing"
                ],
                "career_requirements": [
                    "Analytical fluency with Google Analytics 4 and ad platforms",
                    "Compelling copywriting and content creation abilities",
                    "Campaign budget optimization and Conversion Rate Optimization (CRO)"
                ]
            },
            "Consultant": {
                "overview": "Solves complex strategic and operational challenges for corporate and institutional clients.",
                "learning_objectives": [
                    "Deconstruct business issues using MECE and hypothesis-led frameworks",
                    "Synthesize market research and financial benchmarking data",
                    "Deliver persuasive executive-level presentations"
                ],
                "career_requirements": [
                    "Strong quantitative reasoning and financial valuation acumen",
                    "Top-down problem solving and strategic roadmapping",
                    "Executive presence and client relationship management"
                ]
            },
            "Accountant": {
                "overview": "Prepares and examines financial records, ensuring accuracy, regulatory compliance, and tax efficiency.",
                "learning_objectives": [
                    "Master double-entry bookkeeping and general ledger reconciliation",
                    "Compile balance sheets, income statements, and cash flow reports",
                    "Perform internal controls auditing and statutory tax filings"
                ],
                "career_requirements": [
                    "GAAP / IFRS accounting standards proficiency",
                    "Familiarity with ERP software (SAP, QuickBooks, NetSuite)",
                    "Meticulous attention to detail and quantitative accuracy"
                ]
            },
            "Teacher": {
                "overview": "Instructs students, designs structured curricula, and assesses educational development.",
                "learning_objectives": [
                    "Formulate lesson plans aligned with Bloom's Cognitive Taxonomy",
                    "Utilize active learning and differentiated instructional techniques",
                    "Evaluate learning outcomes via formative and summative metrics"
                ],
                "career_requirements": [
                    "Pedagogical mastery and clear verbal communication",
                    "Classroom leadership and learner engagement techniques",
                    "Adoption of modern EdTech and collaborative digital tools"
                ]
            }
        }

        for c_name, c_data in career_catalog.items():
            self.careers[c_name] = {
                "id": c_name.lower().replace(" ", "_"),
                "name": c_name,
                "overview": c_data["overview"],
                "learning_objectives": c_data["learning_objectives"],
                "career_requirements": c_data["career_requirements"]
            }

        # 2. Detailed Skills & Concepts definitions with prerequisites
        definitions = [
            # Software Engineer
            ("Software Engineer", "Core Programming & OOP", [
                ("c_prog_basics", "Variables, Types & Control Flow", []),
                ("c_oop", "Object-Oriented Programming & Interfaces", ["c_prog_basics"]),
            ]),
            ("Software Engineer", "Data Structures & Algorithms", [
                ("c_dsa_linear", "Arrays, Linked Lists, Stacks & Queues", ["c_prog_basics"]),
                ("c_dsa_trees", "Trees, Graphs & Algorithmic Complexity", ["c_dsa_linear"]),
            ]),
            ("Software Engineer", "System Architecture & APIs", [
                ("c_databases", "Relational Databases & SQL Schema Design", ["c_prog_basics"]),
                ("c_apis", "RESTful API Engineering & Authentication", ["c_oop", "c_databases"]),
                ("c_microservices", "Microservices & Distributed Systems", ["c_apis"])
            ]),

            # Data Analyst
            ("Data Analyst", "Database Querying & SQL", [
                ("c_sql_basics", "SQL Filtering, Grouping & Aggregations", []),
                ("c_sql_advanced", "Advanced SQL Joins, Subqueries & Window Functions", ["c_sql_basics"])
            ]),
            ("Data Analyst", "Data Wrangling & Exploration", [
                ("c_python_pandas", "Data Manipulation with Python & Pandas", ["c_sql_basics"]),
                ("c_eda_stats", "Exploratory Data Analysis & Inferential Statistics", ["c_python_pandas"])
            ]),
            ("Data Analyst", "Data Visualization & BI", [
                ("c_bi_dashboards", "Interactive Dashboards in Tableau/Power BI", ["c_sql_advanced"]),
                ("c_storytelling", "Data Storytelling & Executive Reporting", ["c_bi_dashboards"])
            ]),

            # Web Developer
            ("Web Developer", "Frontend Fundamentals", [
                ("c_html_css", "HTML5 Semantic Markup & CSS3 Flexbox/Grid", []),
                ("c_js_dom", "Modern JavaScript (ES6+), Async & DOM", ["c_html_css"])
            ]),
            ("Web Developer", "Component Frameworks", [
                ("c_react_spa", "Component Architecture & State Management (React)", ["c_js_dom"])
            ]),
            ("Web Developer", "Backend & Deployment", [
                ("c_backend_api", "Server Architecture & REST Endpoints (FastAPI/Node)", ["c_js_dom"]),
                ("c_web_security", "Web Security, HTTPS, and Cloud Deployment", ["c_backend_api"])
            ]),

            # Business Analyst
            ("Business Analyst", "Requirements Engineering", [
                ("c_brd_elicitation", "Stakeholder Elicitation & BRD Documentation", []),
                ("c_user_stories", "Agile User Stories & Acceptance Criteria", ["c_brd_elicitation"])
            ]),
            ("Business Analyst", "Process Modeling", [
                ("c_bpmn_mapping", "BPMN 2.0 Business Process Mapping", ["c_brd_elicitation"])
            ]),
            ("Business Analyst", "Business Data Analysis", [
                ("c_biz_kpis", "KPI Frameworks & Data-Driven Decision Making", ["c_user_stories"])
            ]),

            # Project Manager
            ("Project Manager", "Project Scope & Scheduling", [
                ("c_wbs_scoping", "Scope Definition & Work Breakdown Structure (WBS)", []),
                ("c_schedule_gantt", "Critical Path Method & Gantt Scheduling", ["c_wbs_scoping"])
            ]),
            ("Project Manager", "Agile Execution & Risk", [
                ("c_agile_scrum", "Scrum Ceremonies, Kanban & Sprint Cadences", ["c_wbs_scoping"]),
                ("c_risk_mitigation", "Risk Matrix Analysis & Contingency Planning", ["c_agile_scrum"])
            ]),

            # Graphic Designer
            ("Graphic Designer", "Visual Foundations", [
                ("c_color_typography", "Color Theory, Typography & Composition", []),
                ("c_vector_tools", "Vector Illustration & Digital Assets (Figma/Illustrator)", ["c_color_typography"])
            ]),
            ("Graphic Designer", "UI/UX & Branding", [
                ("c_wireframes", "Wireframing & User Flow Prototyping", ["c_vector_tools"]),
                ("c_brand_systems", "Brand Identity Guidelines & Design Systems", ["c_wireframes"])
            ]),

            # HR Manager
            ("HR Manager", "Talent Acquisition", [
                ("c_recruitment_funnel", "Job Profiling, Sourcing & Interview Rubrics", [])
            ]),
            ("HR Manager", "Employee Relations & Law", [
                ("c_labor_compliance", "Labor Regulations, Ethics & Contract Management", ["c_recruitment_funnel"]),
                ("c_performance_mgmt", "Performance Reviews, OKRs & Employee Retention", ["c_labor_compliance"])
            ]),

            # Marketing Specialist
            ("Marketing Specialist", "Digital Marketing Strategy", [
                ("c_mktg_funnels", "Marketing Funnels & Customer Journey Mapping", []),
                ("c_seo_content", "Search Engine Optimization (SEO) & Content Strategy", ["c_mktg_funnels"])
            ]),
            ("Marketing Specialist", "Performance Marketing", [
                ("c_paid_ads", "PPC Campaigns, Social Ads & Conversion Tracking", ["c_mktg_funnels"]),
                ("c_cro_abtest", "A/B Testing & Conversion Rate Optimization", ["c_paid_ads"])
            ]),

            # Consultant
            ("Consultant", "Strategic Problem Solving", [
                ("c_mece_structuring", "MECE Principle, Issue Trees & Hypothesis Testing", []),
                ("c_market_sizing", "Market Sizing & Competitive Benchmarking", ["c_mece_structuring"])
            ]),
            ("Consultant", "Client Advisory", [
                ("c_exec_synthesis", "Executive Storytelling & Advisory Presentations", ["c_market_sizing"])
            ]),

            # Accountant
            ("Accountant", "Financial Accounting", [
                ("c_bookkeeping", "Double-Entry Bookkeeping & General Ledger", []),
                ("c_financial_stmts", "Preparation of P&L, Balance Sheet & Cash Flow", ["c_bookkeeping"])
            ]),
            ("Accountant", "Tax & Auditing", [
                ("c_taxation", "Corporate Taxation & Compliance Filings", ["c_financial_stmts"]),
                ("c_internal_controls", "Internal Auditing & Fraud Prevention", ["c_financial_stmts"])
            ]),

            # Teacher
            ("Teacher", "Pedagogy & Curriculum", [
                ("c_lesson_planning", "Bloom's Taxonomy & Constructivist Lesson Planning", []),
                ("c_active_learning", "Differentiated Instruction & Student Engagement", ["c_lesson_planning"])
            ]),
            ("Teacher", "Assessment & EdTech", [
                ("c_eval_rubrics", "Formative vs Summative Educational Assessment", ["c_lesson_planning"]),
                ("c_edtech_tools", "Instructional Technology & Collaborative Learning", ["c_active_learning"])
            ]),
        ]

        # Register nodes and edges
        for career_name, skill_name, concept_list in definitions:
            skill_id = skill_name.lower().replace(" ", "_").replace("&", "and")
            self.skills[skill_name] = {"id": skill_id, "name": skill_name, "career": career_name}
            self.career_skills[career_name].append(skill_name)

            for concept_id, concept_title, prereqs in concept_list:
                self.concepts[concept_id] = {
                    "id": concept_id,
                    "title": concept_title,
                    "skill": skill_name,
                    "career": career_name
                }
                self.skill_concepts[skill_name].append(concept_id)
                for prereq_id in prereqs:
                    self.concept_prerequisites[concept_id].append(prereq_id)

        # 3. Learning Resources & Authentic Tutorials
        curated_links = {
            # Software Engineer
            "c_prog_basics": {
                "title": "Python Official Tutorial: Variables, Types & Control Flow",
                "url": "https://docs.python.org/3/tutorial/introduction.html",
                "type": "Official Documentation"
            },
            "c_oop": {
                "title": "Python Official Guide: Classes & Object-Oriented Programming",
                "url": "https://docs.python.org/3/tutorial/classes.html",
                "type": "Official Documentation"
            },
            "c_dsa_linear": {
                "title": "GeeksforGeeks: Linear Data Structures (Arrays & Linked Lists)",
                "url": "https://www.geeksforgeeks.org/data-structures/linked-list/",
                "type": "Interactive Guide"
            },
            "c_dsa_trees": {
                "title": "GeeksforGeeks: Trees, Graphs & Complexity",
                "url": "https://www.geeksforgeeks.org/introduction-to-tree-data-structure/",
                "type": "Interactive Guide"
            },
            "c_databases": {
                "title": "PostgreSQL Tutorial: Relational Databases & SQL Schema Design",
                "url": "https://www.postgresql.org/docs/current/tutorial-sql.html",
                "type": "Official Documentation"
            },
            "c_apis": {
                "title": "FastAPI Official Tutorial: Building RESTful APIs",
                "url": "https://fastapi.tiangolo.com/tutorial/",
                "type": "Official Documentation"
            },
            "c_microservices": {
                "title": "Microservices.io Architecture Pattern Language",
                "url": "https://microservices.io/patterns/microservices.html",
                "type": "Architecture Guide"
            },

            # Data Analyst
            "c_sql_basics": {
                "title": "W3Schools SQL Tutorial: Select, Where & Group By",
                "url": "https://www.w3schools.com/sql/default.asp",
                "type": "Interactive Tutorial"
            },
            "c_sql_advanced": {
                "title": "W3Schools SQL Tutorial: Advanced Joins, Subqueries & Unions",
                "url": "https://www.w3schools.com/sql/sql_join.asp",
                "type": "Interactive Tutorial"
            },
            "c_python_pandas": {
                "title": "Pandas Getting Started: Essential Data Manipulation",
                "url": "https://pandas.pydata.org/docs/getting_started/index.html",
                "type": "Official Documentation"
            },
            "c_eda_stats": {
                "title": "GeeksforGeeks: Exploratory Data Analysis (EDA) in Python",
                "url": "https://www.geeksforgeeks.org/what-is-exploratory-data-analysis/",
                "type": "Hands-On Guide"
            },
            "c_bi_dashboards": {
                "title": "Tableau Visual Best Practices & Dashboard Design",
                "url": "https://help.tableau.com/current/pro/desktop/en-us/visual_best_practices.htm",
                "type": "Official Guide"
            },
            "c_storytelling": {
                "title": "Storytelling with Data: Chart Chooser & Executive Reporting",
                "url": "https://www.storytellingwithdata.com/chart-guide",
                "type": "Design Reference"
            },

            # Web Developer
            "c_html_css": {
                "title": "MDN Web Docs: HTML5 & CSS3 Responsive Layouts",
                "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML",
                "type": "MDN Web Docs"
            },
            "c_js_dom": {
                "title": "MDN Web Docs: Modern JavaScript (ES6+) & DOM",
                "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
                "type": "MDN Web Docs"
            },
            "c_react_spa": {
                "title": "React.dev: Quick Start & Component Architecture",
                "url": "https://react.dev/learn",
                "type": "Official Documentation"
            },
            "c_backend_api": {
                "title": "MDN Web Docs: Express & Node.js Server Architecture",
                "url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs",
                "type": "MDN Web Docs"
            },
            "c_web_security": {
                "title": "MDN Web Docs: Web Security & Protection Guidelines",
                "url": "https://developer.mozilla.org/en-US/docs/Web/Security",
                "type": "MDN Web Docs"
            },

            # Business Analyst
            "c_brd_elicitation": {
                "title": "Modern Analyst: Comprehensive Business Requirements Document (BRD) Guide",
                "url": "https://www.modernanalyst.com/Resources/Articles/tabid/115/ID/1427/Business-Requirements-Document-BRD.aspx",
                "type": "Industry Guide"
            },
            "c_user_stories": {
                "title": "Atlassian Agile Coach: Writing High-Impact User Stories",
                "url": "https://www.atlassian.com/agile/project-management/user-stories",
                "type": "Agile Guide"
            },
            "c_bpmn_mapping": {
                "title": "BPMN.org: Business Process Model and Notation Standards",
                "url": "https://www.bpmn.org/",
                "type": "Industry Standard"
            },
            "c_biz_kpis": {
                "title": "KPI.org: Formulating Key Performance Indicators",
                "url": "https://kpi.org/kpi-basics/",
                "type": "Best Practice Guide"
            },

            # Project Manager
            "c_wbs_scoping": {
                "title": "Project Management Institute (PMI): WBS Practice Standards",
                "url": "https://www.pmi.org/learning/library/work-breakdown-structure-effective-management-5942",
                "type": "PMI Standard"
            },
            "c_schedule_gantt": {
                "title": "Atlassian: Critical Path Method & Gantt Scheduling",
                "url": "https://www.atlassian.com/agile/project-management/gantt-chart",
                "type": "Project Management Guide"
            },
            "c_agile_scrum": {
                "title": "The Official Scrum Guide by Schwaber and Sutherland",
                "url": "https://www.scrumguides.org/scrum-guide.html",
                "type": "Official Standard"
            },
            "c_risk_mitigation": {
                "title": "PMI: Project Risk Analysis & Mitigation Strategies",
                "url": "https://www.pmi.org/learning/library/risk-management-project-success-7006",
                "type": "PMI Standard"
            },

            # Graphic Designer
            "c_color_typography": {
                "title": "Material Design: Color Systems & Typography Scales",
                "url": "https://m3.material.io/styles/color/overview",
                "type": "Design System"
            },
            "c_vector_tools": {
                "title": "Figma Learn: Vector Networks & Digital Asset Creation",
                "url": "https://help.figma.com/hc/en-us/categories/360002042553-Figma-Design",
                "type": "Official Handbook"
            },
            "c_wireframes": {
                "title": "Balsamiq Learn: The Complete Guide to Wireframing",
                "url": "https://balsamiq.com/learn/articles/what-are-wireframes/",
                "type": "UX Guide"
            },
            "c_brand_systems": {
                "title": "DesignSystems.com: Component Libraries & Brand Standards",
                "url": "https://www.designsystems.com/",
                "type": "Design Standards"
            },

            # HR Manager
            "c_recruitment_funnel": {
                "title": "AIHR: The End-to-End Recruitment Process & Talent Sourcing Guide",
                "url": "https://www.aihr.com/blog/recruitment-process/",
                "type": "Professional Guide"
            },
            "c_labor_compliance": {
                "title": "US Department of Labor: Summary of Major Employment Regulations",
                "url": "https://www.dol.gov/general/aboutdol/majorlaws",
                "type": "Statutory Guide"
            },
            "c_performance_mgmt": {
                "title": "Harvard Business Review: The Performance Management Revolution",
                "url": "https://hbr.org/2016/10/the-performance-management-revolution",
                "type": "HBR Executive Review"
            },

            # Marketing Specialist
            "c_mktg_funnels": {
                "title": "Semrush: The Complete Guide to the Marketing Funnel",
                "url": "https://www.semrush.com/blog/marketing-funnel/",
                "type": "Comprehensive Guide"
            },
            "c_seo_content": {
                "title": "Google Search Central: SEO Starter Guide",
                "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
                "type": "Google Documentation"
            },
            "c_paid_ads": {
                "title": "WordStream: Complete Beginner's Guide to Google Ads",
                "url": "https://www.wordstream.com/google-ads",
                "type": "Interactive Guide"
            },
            "c_cro_abtest": {
                "title": "VWO: Complete Guide to A/B Testing & CRO",
                "url": "https://vwo.com/ab-testing/",
                "type": "Conversion Guide"
            },

            # Consultant
            "c_mece_structuring": {
                "title": "MECE Principle: Mutually Exclusive, Collectively Exhaustive Structuring",
                "url": "https://en.wikipedia.org/wiki/MECE_principle",
                "type": "Strategy Framework"
            },
            "c_market_sizing": {
                "title": "Management Consulted: Market Sizing Guide & Formula",
                "url": "https://www.managementconsulted.com/market-sizing/",
                "type": "Consulting Guide"
            },
            "c_exec_synthesis": {
                "title": "Harvard Business Review: How to Give a Stellar Presentation",
                "url": "https://hbr.org/2013/06/how-to-give-a-killer-presentation",
                "type": "Executive Guide"
            },

            # Accountant
            "c_bookkeeping": {
                "title": "Investopedia: Double-Entry Bookkeeping & Accounting Principles",
                "url": "https://www.investopedia.com/terms/d/double-entry.asp",
                "type": "Financial Guide"
            },
            "c_financial_stmts": {
                "title": "Investopedia: Guide to Income Statements, Balance Sheets & Cash Flow",
                "url": "https://www.investopedia.com/terms/f/financial-statements.asp",
                "type": "Financial Guide"
            },
            "c_taxation": {
                "title": "IRS: Small Business & Corporate Taxation Overview",
                "url": "https://www.irs.gov/businesses/small-businesses-self-employed",
                "type": "Regulatory Portal"
            },
            "c_internal_controls": {
                "title": "COSO: Internal Control - Integrated Framework",
                "url": "https://www.coso.org/guidance-on-ic",
                "type": "Accounting Standard"
            },

            # Teacher
            "c_lesson_planning": {
                "title": "Vanderbilt Center for Teaching: Bloom's Taxonomy Guide",
                "url": "https://cft.vanderbilt.edu/guides-sub-pages/blooms-taxonomy/",
                "type": "Pedagogical Guide"
            },
            "c_active_learning": {
                "title": "Yale Poorvu Center: Active Learning & Differentiated Instruction",
                "url": "https://poorvucenter.yale.edu/active-learning",
                "type": "Academic Handbook"
            },
            "c_eval_rubrics": {
                "title": "Carnegie Mellon Eberly Center: Formative vs Summative Assessment",
                "url": "https://www.cmu.edu/teaching/assessment/basics/formative-summative.html",
                "type": "Assessment Guide"
            },
            "c_edtech_tools": {
                "title": "ISTE Standards for Students and Educators",
                "url": "https://www.iste.org/standards",
                "type": "EdTech Standard"
            }
        }

        for cid, cinfo in self.concepts.items():
            res_id = f"res_{cid}"
            link_info = curated_links.get(cid, {
                "title": f"Official Guide: {cinfo['title']}",
                "url": "https://en.wikipedia.org/wiki/" + cinfo['title'].replace(" ", "_"),
                "type": "Reference Guide"
            })
            self.resources[res_id] = {
                "id": res_id,
                "title": link_info["title"],
                "url": link_info["url"],
                "type": link_info["type"],
                "concept_id": cid
            }
            self.resource_concepts[cid].append(res_id)

        # 4. Capstone Projects per career
        project_catalog = {
            "Software Engineer": [
                ("proj_se_1", "Distributed Task Queue & REST API", "Build a scalable worker queue service using FastAPI, Celery, and PostgreSQL.", ["c_apis", "c_databases"]),
                ("proj_se_2", "Microservices E-Commerce Core", "Architect independent microservices with message passing and containerized deployment.", ["c_microservices"])
            ],
            "Data Analyst": [
                ("proj_da_1", "Customer Retention & Churn Dashboard", "Clean 100k customer records, conduct cohort survival analysis, and build a Power BI executive board.", ["c_eda_stats", "c_bi_dashboards"])
            ],
            "Web Developer": [
                ("proj_wd_1", "Full-Stack Collaborative Workspace", "Develop a real-time reactive application with React frontend and FastAPI backend.", ["c_react_spa", "c_backend_api"])
            ],
            "Business Analyst": [
                ("proj_ba_1", "Enterprise Supply Chain Optimization BRD", "Create end-to-end BPMN maps, stakeholder matrices, and user stories for workflow automation.", ["c_bpmn_mapping", "c_user_stories"])
            ],
            "Project Manager": [
                ("proj_pm_1", "Product Launch Sprint Plan & Risk Matrix", "Formulate a complete 6-month cross-functional release roadmap with Gantt charts and risk mitigation plans.", ["c_schedule_gantt", "c_risk_mitigation"])
            ],
            "Graphic Designer": [
                ("proj_gd_1", "Complete Brand Identity & Design System", "Create brand guidelines, typography scale, vector iconography, and interactive prototype in Figma.", ["c_brand_systems", "c_wireframes"])
            ],
            "HR Manager": [
                ("proj_hr_1", "Global Talent Acquisition & Retention Playbook", "Design structured recruitment scorecards, interview loops, and 360-review frameworks.", ["c_performance_mgmt", "c_labor_compliance"])
            ],
            "Marketing Specialist": [
                ("proj_mktg_1", "Multi-Channel Growth Campaign & CRO Audit", "Formulate an omni-channel acquisition funnel with SEO pillar pages and A/B tested landing pages.", ["c_cro_abtest", "c_seo_content"])
            ],
            "Consultant": [
                ("proj_cons_1", "Market Entry & Due Diligence Advisory Report", "Synthesize industry competitive intelligence into a high-impact C-suite advisory presentation.", ["c_exec_synthesis", "c_market_sizing"])
            ],
            "Accountant": [
                ("proj_acc_1", "Comprehensive Financial Audit & Tax Filing Pack", "Reconcile multi-entity general ledgers, prepare financial statements, and verify audit compliance.", ["c_financial_stmts", "c_taxation"])
            ],
            "Teacher": [
                ("proj_teach_1", "Blended Learning Curriculum & Assessment Suite", "Develop a 12-week differentiated instructional syllabus with rubrics and EdTech integration.", ["c_active_learning", "c_eval_rubrics"])
            ]
        }

        for career, proj_list in project_catalog.items():
            for pid, title, desc, conc_ids in proj_list:
                self.projects[pid] = {
                    "id": pid,
                    "title": title,
                    "description": desc,
                    "career": career,
                    "concept_ids": conc_ids
                }
                for cid in conc_ids:
                    self.project_concepts[cid].append(pid)

    # ---------------- Traversal & Analysis Methods ----------------

    def get_career_skills(self, career_name: str) -> List[str]:
        """Returns all skills required by a career."""
        return self.career_skills.get(career_name, [])

    def get_skill_concepts(self, skill_name: str) -> List[str]:
        """Returns all concept IDs involved in a skill."""
        return self.skill_concepts.get(skill_name, [])

    def get_career_concepts(self, career_name: str) -> List[str]:
        """Returns all concept IDs required for a career."""
        concept_ids = []
        skills = self.get_career_skills(career_name)
        for skill in skills:
            concept_ids.extend(self.get_skill_concepts(skill))
        return concept_ids

    def get_prerequisites(self, concept_id: str) -> List[str]:
        """Returns direct prerequisite concept IDs for a given concept."""
        return self.concept_prerequisites.get(concept_id, [])

    def get_all_prerequisites_transitive(self, concept_id: str) -> Set[str]:
        """Traverses and returns all transitive prerequisites with cycle detection."""
        visited = set()
        queue = deque([concept_id])
        
        while queue:
            curr = queue.popleft()
            for prereq in self.get_prerequisites(curr):
                if prereq not in visited:
                    visited.add(prereq)
                    queue.append(prereq)
        return visited

    def detect_cycles(self) -> List[List[str]]:
        """
        Detects if any prerequisite cycles exist in the concept dependency graph.
        Returns list of cycles found (empty list if acyclic).
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {cid: WHITE for cid in self.concepts}
        cycles = []

        def dfs(node, path):
            color[node] = GRAY
            path.append(node)
            for neighbor in self.concept_prerequisites.get(node, []):
                if neighbor in color:
                    if color[neighbor] == GRAY:
                        # Cycle found
                        cycle_idx = path.index(neighbor)
                        cycles.append(path[cycle_idx:] + [neighbor])
                    elif color[neighbor] == WHITE:
                        dfs(neighbor, path)
            path.pop()
            color[node] = BLACK

        for cid in self.concepts:
            if color[cid] == WHITE:
                dfs(cid, [])
        return cycles

    def topological_sort_concepts(self, concept_ids: List[str]) -> List[str]:
        """
        Generates a valid learning order ensuring all prerequisites come before dependents.
        Handles missing nodes and cyclic relationships safely.
        """
        subset = set(concept_ids)
        # In-degree calculation within the subset
        in_degree = {cid: 0 for cid in subset}
        adj = defaultdict(list)

        for cid in subset:
            for prereq in self.get_prerequisites(cid):
                if prereq in subset:
                    adj[prereq].append(cid)
                    in_degree[cid] += 1

        # Kahn's algorithm
        queue = deque([cid for cid in subset if in_degree[cid] == 0])
        ordered = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)
            for dependent in adj[curr]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # If cycles existed, append remaining nodes to prevent truncation
        if len(ordered) < len(subset):
            for cid in subset:
                if cid not in ordered:
                    ordered.append(cid)

        return ordered

    def are_prerequisites_satisfied(self, concept_id: str, mastered_concept_ids: Set[str]) -> bool:
        """Checks if all prerequisite concepts for a given concept are already mastered."""
        prereqs = self.get_prerequisites(concept_id)
        return all(p in mastered_concept_ids for p in prereqs)

knowledge_graph = CareerKnowledgeGraph()
