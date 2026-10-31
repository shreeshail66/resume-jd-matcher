"""Skill vocabulary used for keyword extraction.

Add your own skills to SKILL_CATEGORIES and aliases to ALIASES.
Everything is matched in lowercase, so write skills in lowercase.
"""

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "golang",
        "ruby", "php", "swift", "kotlin", "scala", "rust", "matlab", "bash",
    ],
    "Web & Frontend": [
        "html", "css", "react", "angular", "vue", "next.js", "redux",
        "tailwind", "bootstrap", "jquery", "webpack",
    ],
    "Backend & APIs": [
        "node.js", "express", "django", "flask", "fastapi", "spring boot",
        ".net", "rest api", "graphql", "microservices", "grpc",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
        "nosql", "elasticsearch", "cassandra", "dynamodb", "snowflake",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "ci/cd", "github actions", "ansible", "linux", "git", "nginx",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "spark", "hadoop", "airflow", "tableau", "power bi", "excel",
        "data analysis", "data visualization", "statistics", "etl",
        "feature engineering", "llm", "transformers", "tf-idf", "opencv",
    ],
    "Testing & Practices": [
        "unit testing", "pytest", "selenium", "junit", "tdd", "agile",
        "scrum", "jira", "code review", "system design", "oop",
        "data structures", "algorithms",
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "collaboration", "mentoring", "stakeholder management",
        "project management", "time management", "critical thinking",
    ],
}

# canonical skill -> other ways people write it
ALIASES = {
    "javascript": ["js", "ecmascript", "es6"],
        "golang": ["go lang"],
    "react": ["react.js", "reactjs"],
    "vue": ["vue.js", "vuejs"],
    "angular": ["angularjs"],
    "node.js": ["nodejs", "node js"],
    "express": ["express.js", "expressjs"],
    "next.js": ["nextjs"],
    "postgresql": ["postgres"],
    "mongodb": ["mongo"],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "ci/cd": ["cicd", "ci cd", "continuous integration", "continuous delivery"],
    "machine learning": ["ml"],
        "nlp": ["natural language processing"],
        "scikit-learn": ["sklearn", "scikit learn"],
        "power bi": ["powerbi"],
    "rest api": ["rest apis", "restful", "restful api", "restful apis"],
    "llm": ["llms", "large language model", "large language models"],
    "tf-idf": ["tfidf"],
    "oop": ["object oriented", "object-oriented"],
    "data structures": ["dsa"],
    "unit testing": ["unit tests"],
    "problem solving": ["problem-solving"],
    "teamwork": ["team player", "team work"],
    "data visualization": ["data visualisation"],
    "github actions": ["gh actions"],
    "spring boot": ["springboot"],
    ".net": ["dotnet", "asp.net"],
}

# flat list + reverse lookup (skill -> category)
SKILLS = [s for group in SKILL_CATEGORIES.values() for s in group]
SKILL_TO_CATEGORY = {s: cat for cat, group in SKILL_CATEGORIES.items() for s in group}
