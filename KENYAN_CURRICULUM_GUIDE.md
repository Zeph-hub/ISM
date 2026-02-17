# Kenyan Education System Curriculum Models

## Overview

The updated curriculum service models support both the **Competency-Based Curriculum (CBC)** and **British Curriculum** frameworks as implemented in Kenyan schools, aligned with the Ministry of Education, Science and Technology (MoEST) guidelines.

---

## Curriculum Frameworks

### 1. Competency-Based Curriculum (CBC)

The CBC is the new national curriculum framework introduced in Kenya, emphasizing:
- **Learner-centered approach**: Focus on learner acquisition of competencies
- **Life skills development**: Integration of generic/transferable skills
- **Holistic development**: Seven pillars of education
- **Competency-based assessment**: Moving away from traditional grades

#### CBC Levels

```
ECD (Early Childhood Development)
├─ Ages 3-4: PP1 (Pre-Primary 1)
└─ Ages 4-5: PP2 (Pre-Primary 2)

Primary
├─ Ages 5-6: Grade 1
├─ Ages 6-7: Grade 2
├─ Ages 7-8: Grade 3
├─ Ages 8-9: Grade 4
├─ Ages 9-10: Grade 5
└─ Ages 10-11: Grade 6

Lower Secondary (Grades 7-9)
├─ Ages 12-13: Grade 7
├─ Ages 13-14: Grade 8
└─ Ages 14-15: Grade 9

Upper Secondary (Grades 10-12)
├─ Ages 15-16: Grade 10
├─ Ages 16-17: Grade 11
└─ Ages 17-18: Grade 12
```

#### The Seven Pillars of CBC Education

1. **Literacy & Numeracy**: Foundation for all learning
2. **Science & Technology**: Understanding the physical world
3. **Social Emotional**: Personal and interpersonal development
4. **Physical & Health Education**: Wellbeing and fitness
5. **Creative & Cultural**: Artistic and cultural expression
6. **Moral & Ethics**: Values and citizenship
7. **Financial Literacy**: Economic understanding and decision-making

#### CBC Learning Areas

```python
class LearningAreaType(str, Enum):
    LANGUAGES = "languages"                        # Swahili, English, Other Languages
    MATHEMATICS = "mathematics"
    SCIENCE_TECHNOLOGY = "science_technology"      # Encompasses Physics, Chemistry, Biology
    SOCIAL_STUDIES = "social_studies"
    BUSINESS_STUDIES = "business_studies"
    AGRICULTURAL_SCIENCES = "agricultural_sciences"
    VISUAL_PERFORMING_ARTS = "visual_performing_arts"
    PHYSICAL_HEALTH_EDUCATION = "physical_health_education"
```

#### CBC Competencies

- **Core Competencies**: Essential for all learners (Communication, Collaboration, Critical Thinking, etc.)
- **Subject-Specific Competencies**: Unique to each learning area
- **Proficiency Levels**: 1-5 scale indicating mastery depth

#### CBC Grading System

```
E - Exceeds Expectations (90-100%)    → Learner exceeds the required standard
M - Meets Expectations (70-89%)       → Learner meets the required standard
A - Approaches Expectations (50-69%)  → Learner is approaching the standard
B - Below Expectations (< 50%)        → Learner has not yet met the standard
```

#### Key CBC Components

**Competency Model**:
```python
class Competency(BaseModel):
    code: str                    # e.g., "CBC-001"
    title: str                   # Competency name
    description: str             # What the learner should be able to do
    learning_area: LearningAreaType
    pillar: PillarType
    core_competency: bool        # TRUE if mandatory for all learners
    proficiency_level: int       # 1-5 scale
```

**Learning Outcomes**:
- Specific, measurable targets derived from competencies
- Assessment methods: Observation, Projects, Tests, Portfolios

**Generic Skills** (Transferable Skills):
- Critical Thinking
- Creativity & Imagination
- Communication
- Collaboration
- Leadership
- Problem-solving
- Emotional Intelligence

---

### 2. British Curriculum

The British curriculum framework is used in select schools offering international qualifications:
- **IGCSE**: International General Certificate of Secondary Education
- **A-Levels**: Advanced Level qualifications
- **Focus**: Subject-based learning with standardized assessments

#### British Levels

```
Primary (Years 1-6): Foundation knowledge
Secondary (Years 7-9): Preparation for IGCSE
IGCSE (Grades 10-11): International certificates in specific subjects
A-Levels (Grades 12-13): Advanced qualifications for university entry
AS-Levels: Alternative to A-Levels (Year 12)
```

#### British Grading System

```
A* (90-100%)    → Outstanding
A (80-89%)      → Excellent
B (70-79%)      → Good
C (60-69%)      → Satisfactory
D (50-59%)      → Acceptable
E (40-49%)      → Below Average
F (< 40%)       → Poor
```

#### Exam Boards

Common exam boards in Kenya:
- `Cambridge` (University of Cambridge International Examinations)
- `Edexcel` (Pearson Edexcel)
- `Oxford AQA`

#### British Curriculum Structure

**Subject Model**:
```python
class Subject(BaseModel):
    code: str                    # e.g., "MATH", "PHYS"
    title: str                   # Subject name
    british_level: BritishLevel  # Level offered
    exam_board: str              # Cambridge, Edexcel, etc.
```

**Topic Hierarchy**:
```
Subject
├─ Topic 1
│  ├─ Subtopic 1.1
│  │  ├─ Learning Objective 1
│  │  └─ Learning Objective 2
│  └─ Subtopic 1.2
└─ Topic 2
```

---

## Key Model Differences

| Feature | CBC | British |
|---------|-----|---------|
| **Assessment** | Competency-based | Grade-based exams |
| **Focus** | Holistic development | Subject mastery |
| **Grades** | 4 levels (E, M, A, B) | 7 levels (A*, A, B, C, D, E, F) |
| **Learning Model** | Learner-centered | Subject-centered |
| **Skills Focus** | Generic + Specific | Subject-specific |
| **Progress Tracking** | Competency progress | Subject grades |

---

## Main Models

### CBC Models

#### 1. Competency & Learning Outcomes
```python
# Define what learners should know/do
competency = Competency(
    code="LIT-001",
    title="Demonstrates literacy proficiency",
    learning_area=LearningAreaType.LANGUAGES,
    pillar=PillarType.LITERACY_NUMERACY,
    core_competency=True,
    proficiency_level=3
)

# Specific measurable outcomes
outcome = LearningOutcome(
    competency_id=1,
    description="Learner reads and comprehends grade-level texts",
    assessment_method="project"  # or "observation", "test"
)
```

#### 2. Generic Skills
```python
skill = GenericSkill(
    name="Critical Thinking",
    category="Cognitive",
    description="Ability to analyze and evaluate information"
)
```

#### 3. CBC Course
```python
# A course combining competencies and skills
cbc_course = CBCCourse(
    code="LAN-GR7-001",
    title="Languages (Grade 7)",
    learning_area=LearningAreaType.LANGUAGES,
    cbc_level=CBCLevel.LOWER_SECONDARY,
    duration_weeks=14,
    competencies=[1, 2, 3],  # Competency IDs
    generic_skills=[1, 2]     # Skill IDs
)
```

#### 4. CBC Curriculum Package
```python
# Entire curriculum for a level
curriculum = CBCCurriculum(
    name="Lower Secondary CBC 2024",
    cbc_level=CBCLevel.LOWER_SECONDARY,
    version="1.0",
    academic_year=2024,
    courses=[1, 2, 3, 4, 5, 6, 7, 8]  # Course IDs
)
```

#### 5. Student Competency Progress
```python
# Track student progress toward competency mastery
progress = CompetencyProgress(
    student_id=101,
    competency_id=1,
    status=CompetencyStatus.ACHIEVED,
    proficiency_level=3,
    last_assessed=datetime.now()
)
```

#### 6. CBC Progress Report
```python
# Comprehensive student progress report for CBC
report = CBCProgressReport(
    student_id=101,
    reporting_period="Term 1 2024",
    curriculum_type=CurriculumFramework.CBC,
    competencies_achieved=[...],
    generic_skills_progress={1: 85.0, 2: 75.0},
    pillar_scores={
        "literacy_numeracy": 78,
        "science_technology": 82,
        ...
    },
    overall_performance="Good",
    teacher_comments="..."
)
```

### British Curriculum Models

#### 1. Subject
```python
subject = Subject(
    code="MATH",
    title="Mathematics",
    british_level=BritishLevel.IGCSE,
    exam_board="Cambridge",
    instructor_id=10
)
```

#### 2. Topics & Subtopics
```python
# Organize content hierarchically
topic = Topic(
    subject_id=1,
    title="Algebra",
    order=1
)

subtopic = Subtopic(
    topic_id=1,
    title="Linear Equations",
    learning_objectives=[
        "Solve linear equations with one variable",
        "Solve simultaneous equations",
        "Graphing linear equations"
    ],
    order=1
)
```

#### 3. British Course
```python
# A course offering a subject at a specific level
course = BritishCourse(
    code="IGCSE-MATH-2024",
    subject_id=1,
    title="IGCSE Mathematics 2024",
    british_level=BritishLevel.IGCSE,
    exam_board="Cambridge",
    duration_weeks=36,
    instructor_id=10
)
```

#### 4. British Curriculum Package
```python
curriculum = BritishCurriculum(
    name="IGCSE Programme 2024",
    british_level=BritishLevel.IGCSE,
    exam_board="Cambridge",
    version="1.0",
    academic_year=2024,
    subjects=[1, 2, 3, 4, 5]  # Subject IDs
)
```

#### 5. British Progress Report
```python
report = BritishProgressReport(
    student_id=101,
    reporting_period="Term 2 2024",
    curriculum_type=CurriculumFramework.BRITISH,
    subject_grades={
        1: "A*",  # Mathematics
        2: "A",   # English
        3: "B"    # Physics
    },
    predicted_grades={
        1: "A*",
        2: "A",
        3: "A"
    },
    teacher_comments="Excellent progress..."
)
```

---

## Shared Models

### Learning Resources
```python
resource = LearningResource(
    title="Photosynthesis Simulation",
    resource_type=ResourceType.INTERACTIVE,
    url="https://example.com/photosynthesis",
    cbc_course_id=1,  # Can link to either curriculum type
    british_course_id=None
)
```

### Assessments
```python
# Used by both curriculum types
assessment = Assessment(
    title="End of Unit Test",
    description="Assessment of unit learning",
    assessment_type="summative",
    max_score=100.0,
    duration_minutes=60,
    cbc_course_id=1
)

# Student takes assessment
student_result = StudentAssessment(
    student_id=101,
    assessment_id=1,
    score=78.5,
    competencies_achieved=[1, 2],  # For CBC
    grade="M/A"
)
```

---

## Best Practices for Kenyan Schools

### CBC Implementation

1. **Competency Definition**
   - Clearly define what learners should be able to do
   - Link to one of the seven pillars
   - Ensure measurable outcomes

2. **Assessment Methods**
   - Use formative assessment (observation, projects)
   - Include summative assessments
   - Portfolio-based evidence collection

3. **Reporting**
   - Use 4-level grading system (E, M, A, B)
   - Track competency progression
   - Include generic skills development

4. **Differentiation**
   - Support varying competency levels
   - Provide scaffolding for struggling learners
   - Enrich for high achievers

### British Curriculum Implementation

1. **Exam Board Alignment**
   - Ensure content matches exam board specifications
   - Use official syllabus documents
   - Regular exam board training for teachers

2. **Continuous Assessment**
   - Regular formative assessments
   - Mock exams before final exams
   - Detailed marking schemes

3. **Progression Tracking**
   - Monitor subject-specific progress
   - Predicted grades based on assessment
   - Intervention for at-risk students

4. **Resources**
   - Access to quality learning materials
   - Laboratory equipment for sciences
   - Past papers for practice

---

## API Endpoints Structure

### CBC Endpoints
```
POST   /api/curriculum/cbc-curricula          # Create CBC curriculum
GET    /api/curriculum/cbc-curricula          # List CBC curricula
GET    /api/curriculum/cbc-curricula/{id}    # Get CBC curriculum with courses

POST   /api/curriculum/cbc-courses            # Create CBC course
GET    /api/curriculum/cbc-courses/{id}      # Get CBC course with details

POST   /api/curriculum/competencies           # Create competency
GET    /api/curriculum/competencies/{id}     # Get competency

POST   /api/curriculum/competency-progress    # Track student progress
GET    /api/curriculum/competency-progress/{student_id}

POST   /api/curriculum/cbc-reports/{student_id}  # Generate CBC progress report
```

### British Endpoints
```
POST   /api/curriculum/british-curricula      # Create British curriculum
GET    /api/curriculum/british-curricula      # List British curricula

POST   /api/curriculum/subjects               # Create subject
GET    /api/curriculum/subjects/{id}          # Get subject with topics

POST   /api/curriculum/british-courses        # Create British course
GET    /api/curriculum/british-courses/{id}   # Get course with topics

POST   /api/curriculum/british-reports/{student_id}  # Generate progress report
```

---

## Migration from Old to New Model

If you have existing data in the generic `Course` model:

1. **Identify Curriculum Type**: Determine if course is CBC or British
2. **Migrate to Specific Model**: Move to `CBCCourse` or `BritishCourse`
3. **Map Learning Areas**: For CBC, assign to appropriate learning area
4. **Update Topics**: Break down generic modules into CBC competencies or British topics

---

## References

- [Kenya Ministry of Education CBC Framework](https://www.education.go.ke)
- [Cambridge International](https://www.cambridgeinternational.org)
- [BBC Learning](https://www.bbc.co.uk/bitesize)
- [Khan Academy (Free Resources)](https://www.khanacademy.org)
