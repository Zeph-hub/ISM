"""
Curriculum Service Models - Kenyan Education System
Supports both CBC (Competency-Based Curriculum) and British Curriculum
as per Ministry of Education, Science and Technology guidelines.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===== ENUMS FOR CURRICULUM TYPES =====
class CurriculumFramework(str, Enum):
    """Curriculum framework types in Kenya"""
    CBC = "cbc"  # Competency-Based Curriculum
    BRITISH = "british"  # British curriculum (IGCSE, A-Levels)


class CBCLevel(str, Enum):
    """CBC Levels according to MoE"""
    ECD = "ecd"  # Early Childhood Development (Ages 3-5)
    PRIMARY = "primary"  # Classes 1-6 (Ages 6-12)
    LOWER_SECONDARY = "lower_secondary"  # Grades 7-9 (Ages 13-15)
    UPPER_SECONDARY = "upper_secondary"  # Grades 10-12 (Ages 16-18)


class BritishLevel(str, Enum):
    """British Curriculum Levels"""
    PRIMARY = "primary"  # Years 1-6
    SECONDARY = "secondary"  # Years 7-9
    IGCSE = "igcse"  # International GCSE
    A_LEVEL = "a_level"  # A-Levels
    AS_LEVEL = "as_level"  # AS-Levels


class CBCGrade(str, Enum):
    """CBC Grading system"""
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"  # E - 90-100%
    MEETS_EXPECTATIONS = "meets_expectations"  # M - 70-89%
    APPROACHES_EXPECTATIONS = "approaches_expectations"  # A - 50-69%
    BELOW_EXPECTATIONS = "below_expectations"  # B - Below 50%


class BritishGrade(str, Enum):
    """British Grading system (IGCSE/A-Levels)"""
    GRADE_A_STAR = "a*"  # 90-100%
    GRADE_A = "a"  # 80-89%
    GRADE_B = "b"  # 70-79%
    GRADE_C = "c"  # 60-69%
    GRADE_D = "d"  # 50-59%
    GRADE_E = "e"  # 40-49%
    GRADE_F = "f"  # Below 40%


class PillarType(str, Enum):
    """CBC Seven Pillars of Education"""
    LITERACY_NUMERACY = "literacy_numeracy"
    SCIENCE_TECHNOLOGY = "science_technology"
    SOCIAL_EMOTIONAL = "social_emotional"
    PHYSICAL_HEALTH = "physical_health"
    CREATIVE_CULTURAL = "creative_cultural"
    MORAL_ETHICS = "moral_ethics"
    FINANCIAL_LITERACY = "financial_literacy"


class LearningAreaType(str, Enum):
    """CBC Learning Areas"""
    LANGUAGES = "languages"
    MATHEMATICS = "mathematics"
    SCIENCE_TECHNOLOGY = "science_technology"
    SOCIAL_STUDIES = "social_studies"
    BUSINESS_STUDIES = "business_studies"
    AGRICULTURAL_SCIENCES = "agricultural_sciences"
    VISUAL_PERFORMING_ARTS = "visual_performing_arts"
    PHYSICAL_HEALTH_EDUCATION = "physical_health_education"


class ResourceType(str, Enum):
    """Learning resource types"""
    TEXT_DOCUMENT = "text_document"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    IMAGE = "image"
    PRESENTATION = "presentation"
    LINK = "link"


class CompetencyStatus(str, Enum):
    """Competency achievement status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    MASTERED = "mastered"


class CurriculumStatus(str, Enum):
    """Curriculum status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# ===== CBC MODELS =====
class CompetencyBase(BaseModel):
    """Base CBC competency model"""
    code: str  # e.g., "CBC-001"
    title: str
    description: str
    learning_area: LearningAreaType
    pillar: PillarType


class CompetencyCreate(CompetencyBase):
    """Create competency"""
    core_competency: bool = False
    proficiency_level: int = 1  # 1-5 levels


class Competency(CompetencyBase):
    """Competency response model"""
    id: int
    core_competency: bool
    proficiency_level: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningOutcomeBase(BaseModel):
    """Learning outcome for CBC"""
    competency_id: int
    description: str
    assessment_method: str  # e.g., "observation", "project", "test"


class LearningOutcomeCreate(LearningOutcomeBase):
    """Create learning outcome"""
    pass


class LearningOutcome(LearningOutcomeBase):
    """Learning outcome response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GenericSkillBase(BaseModel):
    """Generic/Transferable skills in CBC"""
    name: str  # e.g., "Critical Thinking", "Communication"
    description: Optional[str] = None
    category: str  # e.g., "Cognitive", "Interpersonal", "Intrapersonal"


class GenericSkillCreate(GenericSkillBase):
    """Create generic skill"""
    pass


class GenericSkill(GenericSkillBase):
    """Generic skill response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CBCCourseBase(BaseModel):
    """Base CBC course model"""
    code: str
    title: str
    description: Optional[str] = None
    learning_area: LearningAreaType
    cbc_level: CBCLevel
    duration_weeks: int


class CBCCourseCreate(CBCCourseBase):
    """Create CBC course"""
    instructor_id: int
    competencies: List[int] = []  # Competency IDs
    generic_skills: List[int] = []  # Generic skill IDs


class CBCCourse(CBCCourseBase):
    """CBC course response model"""
    id: int
    instructor_id: int
    status: CurriculumStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CBCCourseWithDetails(CBCCourse):
    """CBC course with competencies and skills"""
    competencies: List[Competency] = []
    learning_outcomes: List[LearningOutcome] = []
    generic_skills: List[GenericSkill] = []


# ===== BRITISH CURRICULUM MODELS =====
class SubjectBase(BaseModel):
    """British curriculum subject"""
    code: str  # e.g., "MATH", "PHYS"
    title: str
    description: Optional[str] = None
    british_level: BritishLevel


class SubjectCreate(SubjectBase):
    """Create subject"""
    instructor_id: int
    exam_board: Optional[str] = None  # e.g., "Cambridge", "Edexcel"


class Subject(SubjectBase):
    """Subject response model"""
    id: int
    instructor_id: int
    exam_board: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    """Topic under a British subject"""
    subject_id: int
    title: str
    description: Optional[str] = None
    order: int


class TopicCreate(TopicBase):
    """Create topic"""
    pass


class Topic(TopicBase):
    """Topic response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubtopicBase(BaseModel):
    """Subtopic under a British subject topic"""
    topic_id: int
    title: str
    learning_objectives: List[str]  # e.g., ["Understand photosynthesis", "Explain...]
    order: int


class SubtopicCreate(SubtopicBase):
    """Create subtopic"""
    pass


class Subtopic(SubtopicBase):
    """Subtopic response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BritishCourseBase(BaseModel):
    """Base British curriculum course"""
    code: str
    subject_id: int
    title: str
    description: Optional[str] = None
    british_level: BritishLevel
    duration_weeks: int


class BritishCourseCreate(BritishCourseBase):
    """Create British course"""
    instructor_id: int
    exam_board: Optional[str] = None


class BritishCourse(BritishCourseBase):
    """British course response model"""
    id: int
    instructor_id: int
    status: CurriculumStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BritishCourseWithDetails(BritishCourse):
    """British course with topics and resources"""
    subject: Optional[Subject] = None
    topics: List[Topic] = []


# ===== SHARED MODELS =====
class LearningResourceBase(BaseModel):
    """Learning resource for both curricula"""
    title: str
    description: Optional[str] = None
    resource_type: ResourceType
    url: Optional[str] = None
    file_path: Optional[str] = None
    cbc_course_id: Optional[int] = None  # Link to CBC course
    british_course_id: Optional[int] = None  # Link to British course


class LearningResourceCreate(LearningResourceBase):
    """Create learning resource"""
    pass


class LearningResource(LearningResourceBase):
    """Learning resource response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    """Assessment for both CBC and British"""
    title: str
    description: str
    assessment_type: str  # "formative", "summative", "diagnostic"
    max_score: float
    duration_minutes: int
    cbc_course_id: Optional[int] = None
    british_course_id: Optional[int] = None


class AssessmentCreate(AssessmentBase):
    """Create assessment"""
    pass


class Assessment(AssessmentBase):
    """Assessment response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentAssessmentBase(BaseModel):
    """Student assessment result"""
    student_id: int
    assessment_id: int
    score: float
    competencies_achieved: Optional[List[int]] = None  # For CBC
    comments: Optional[str] = None


class StudentAssessmentCreate(StudentAssessmentBase):
    """Create student assessment"""
    submitted_at: datetime


class StudentAssessment(StudentAssessmentBase):
    """Student assessment response model"""
    id: int
    grade: Optional[str] = None  # CBC or British grade
    submitted_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompetencyProgressBase(BaseModel):
    """Track student CBC competency progress"""
    student_id: int
    competency_id: int
    status: CompetencyStatus
    proficiency_level: int  # 0-5 levels


class CompetencyProgressCreate(CompetencyProgressBase):
    """Create competency progress"""
    pass


class CompetencyProgress(CompetencyProgressBase):
    """Competency progress response model"""
    id: int
    last_assessed: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CBCCurriculumBase(BaseModel):
    """Base CBC curriculum package"""
    name: str  # e.g., "Lower Secondary CBC 2023"
    description: Optional[str] = None
    version: str
    cbc_level: CBCLevel
    academic_year: int  # e.g., 2024


class CBCCurriculumCreate(CBCCurriculumBase):
    """Create CBC curriculum"""
    courses: List[int] = []  # CBC course IDs


class CBCCurriculum(CBCCurriculumBase):
    """CBC curriculum response model"""
    id: int
    status: CurriculumStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class CBCCurriculumWithCourses(CBCCurriculum):
    """CBC curriculum with courses"""
    courses: List[CBCCourse] = []


class BritishCurriculumBase(BaseModel):
    """Base British curriculum package"""
    name: str  # e.g., "IGCSE 2024"
    description: Optional[str] = None
    version: str
    british_level: BritishLevel
    exam_board: str  # e.g., "Cambridge"
    academic_year: int


class BritishCurriculumCreate(BritishCurriculumBase):
    """Create British curriculum"""
    subjects: List[int] = []  # Subject IDs


class BritishCurriculum(BritishCurriculumBase):
    """British curriculum response model"""
    id: int
    status: CurriculumStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class BritishCurriculumWithSubjects(BritishCurriculum):
    """British curriculum with subjects"""
    subjects: List[Subject] = []


# ===== PROGRESS & REPORTING =====
class ProgressReportBase(BaseModel):
    """Student progress report"""
    student_id: int
    reporting_period: str  # e.g., "Term 1 2024"
    curriculum_type: CurriculumFramework


class CBCProgressReport(ProgressReportBase):
    """CBC student progress report"""
    competencies_achieved: List[CompetencyProgress]
    generic_skills_progress: dict  # {skill_id: progress_percentage}
    pillar_scores: dict  # {pillar: score}
    overall_performance: str
    teacher_comments: Optional[str] = None


class BritishProgressReport(ProgressReportBase):
    """British curriculum progress report"""
    subject_grades: dict  # {subject_id: grade}
    predicted_grades: dict  # {subject_id: predicted_grade}
    exam_performance: Optional[dict] = None
    teacher_comments: Optional[str] = None


# ===== LEGACY MODELS (For backward compatibility) =====
class CourseStatus(str, Enum):
    """Course status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class CourseBase(BaseModel):
    """Base course model - Generic"""
    code: str
    title: str
    description: Optional[str] = None
    level: str
    credit_hours: int


class CourseCreate(CourseBase):
    """Course creation model"""
    instructor_id: int
    prerequisites: Optional[List[int]] = []


class CourseUpdate(BaseModel):
    """Course update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    credit_hours: Optional[int] = None
    instructor_id: Optional[int] = None


class Course(CourseBase):
    """Course response model"""
    id: int
    instructor_id: int
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourseWithStudents(Course):
    """Course with enrolled students"""
    enrolled_students: List[dict] = []


class ModuleBase(BaseModel):
    """Base module model"""
    course_id: int
    title: str
    description: Optional[str] = None
    order: int


class ModuleCreate(ModuleBase):
    """Module creation model"""
    pass


class Module(ModuleBase):
    """Module response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    """Base lesson model"""
    module_id: int
    title: str
    content: str
    order: int


class LessonCreate(LessonBase):
    """Lesson creation model"""
    pass


class Lesson(LessonBase):
    """Lesson response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssignmentLegacyBase(BaseModel):
    """Base assignment model - Legacy"""
    course_id: int
    title: str
    description: str
    due_date: datetime


class AssignmentLegacyCreate(AssignmentLegacyBase):
    """Assignment creation model"""
    max_score: float


class AssignmentLegacy(AssignmentLegacyBase):
    """Assignment response model"""
    id: int
    max_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResourceBase(BaseModel):
    """Base learning resource model"""
    course_id: int
    title: str
    resource_type: str  # "document", "video", "link", etc.
    url: str


class ResourceCreate(ResourceBase):
    """Resource creation model"""
    pass


class Resource(ResourceBase):
    """Resource response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CurriculumBase(BaseModel):
    """Base curriculum model"""
    name: str
    description: Optional[str] = None
    version: str


class CurriculumCreate(CurriculumBase):
    """Curriculum creation model"""
    courses: List[int] = []  # List of course IDs


class Curriculum(CurriculumBase):
    """Curriculum response model"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CurriculumWithCourses(Curriculum):
    """Curriculum with its courses"""
    courses: List[Course] = []
