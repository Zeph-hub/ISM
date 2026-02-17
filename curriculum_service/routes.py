from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from .models import (
    # CBC Models
    Competency, CompetencyCreate, LearningOutcome, LearningOutcomeCreate,
    GenericSkill, GenericSkillCreate, CBCCourse, CBCCourseCreate,
    CBCCourseWithDetails, CBCCurriculum, CBCCurriculumCreate,
    CBCCurriculumWithCourses, CompetencyProgress, CompetencyProgressCreate,
    CBCProgressReport, CompetencyStatus, CBCLevel, LearningAreaType,
    # British Models
    Subject, SubjectCreate, Topic, TopicCreate, Subtopic, SubtopicCreate,
    BritishCourse, BritishCourseCreate, BritishCourseWithDetails,
    BritishCurriculum, BritishCurriculumCreate, BritishCurriculumWithSubjects,
    BritishProgressReport, BritishLevel,
    # Shared Models
    Assessment, AssessmentCreate, StudentAssessment, StudentAssessmentCreate,
    LearningResource, LearningResourceCreate, CurriculumStatus
)

# Mock databases
COMPETENCIES_DB = {}
LEARNING_OUTCOMES_DB = {}
GENERIC_SKILLS_DB = {}
CBC_COURSES_DB = {}
CBC_CURRICULA_DB = {}
COMPETENCY_PROGRESS_DB = {}

SUBJECTS_DB = {}
TOPICS_DB = {}
SUBTOPICS_DB = {}
BRITISH_COURSES_DB = {}
BRITISH_CURRICULA_DB = {}

ASSESSMENTS_DB = {}
STUDENT_ASSESSMENTS_DB = {}
RESOURCES_DB = {}

COMPETENCY_ID_COUNTER = 1
OUTCOME_ID_COUNTER = 1
SKILL_ID_COUNTER = 1
CBC_COURSE_ID_COUNTER = 1
CBC_CURRICULUM_ID_COUNTER = 1
SUBJECT_ID_COUNTER = 1
TOPIC_ID_COUNTER = 1
SUBTOPIC_ID_COUNTER = 1
BRITISH_COURSE_ID_COUNTER = 1
ASSESSMENT_ID_COUNTER = 1

router = APIRouter(prefix="/api/curriculum", tags=["Curriculum"])


# ===== CBC COMPETENCIES =====
@router.post("/cbc/competencies", response_model=Competency, status_code=status.HTTP_201_CREATED)
async def create_competency(competency_data: CompetencyCreate) -> Competency:
    """
    Create a CBC competency.
    
    **Best Practice**: Ensure competency codes are unique and descriptive
    """
    global COMPETENCY_ID_COUNTER
    
    # Check unique code
    if any(c["code"] == competency_data.code for c in COMPETENCIES_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Competency code {competency_data.code} already exists"
        )
    
    competency_id = COMPETENCY_ID_COUNTER
    COMPETENCY_ID_COUNTER += 1
    
    new_competency = {
        "id": competency_id,
        "code": competency_data.code,
        "title": competency_data.title,
        "description": competency_data.description,
        "learning_area": competency_data.learning_area,
        "pillar": competency_data.pillar,
        "core_competency": competency_data.core_competency,
        "proficiency_level": competency_data.proficiency_level,
        "created_at": datetime.utcnow()
    }
    
    COMPETENCIES_DB[competency_id] = new_competency
    return Competency(**new_competency)


@router.get("/cbc/competencies", response_model=List[Competency])
async def list_competencies(
    skip: int = 0,
    limit: int = 10,
    learning_area: Optional[str] = None,
    core_only: bool = False
) -> List[Competency]:
    """List CBC competencies with filtering."""
    competencies = list(COMPETENCIES_DB.values())
    
    if learning_area:
        competencies = [c for c in competencies if c["learning_area"] == learning_area]
    
    if core_only:
        competencies = [c for c in competencies if c["core_competency"]]
    
    competencies = competencies[skip:skip + limit]
    return [Competency(**c) for c in competencies]


@router.get("/cbc/competencies/{competency_id}", response_model=Competency)
async def get_competency(competency_id: int) -> Competency:
    """Get a specific competency."""
    competency = COMPETENCIES_DB.get(competency_id)
    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competency not found"
        )
    return Competency(**competency)


# ===== LEARNING OUTCOMES =====
@router.post("/cbc/competencies/{competency_id}/outcomes", response_model=LearningOutcome, status_code=status.HTTP_201_CREATED)
async def create_learning_outcome(competency_id: int, outcome_data: LearningOutcomeCreate) -> LearningOutcome:
    """Create a learning outcome for a competency."""
    competency = COMPETENCIES_DB.get(competency_id)
    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competency not found"
        )
    
    global OUTCOME_ID_COUNTER
    outcome_id = OUTCOME_ID_COUNTER
    OUTCOME_ID_COUNTER += 1
    
    new_outcome = {
        "id": outcome_id,
        "competency_id": competency_id,
        "description": outcome_data.description,
        "assessment_method": outcome_data.assessment_method,
        "created_at": datetime.utcnow()
    }
    
    LEARNING_OUTCOMES_DB[outcome_id] = new_outcome
    return LearningOutcome(**new_outcome)


@router.get("/cbc/competencies/{competency_id}/outcomes", response_model=List[LearningOutcome])
async def list_learning_outcomes(competency_id: int) -> List[LearningOutcome]:
    """Get all learning outcomes for a competency."""
    competency = COMPETENCIES_DB.get(competency_id)
    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competency not found"
        )
    
    outcomes = [o for o in LEARNING_OUTCOMES_DB.values() if o["competency_id"] == competency_id]
    return [LearningOutcome(**o) for o in outcomes]


# ===== GENERIC SKILLS =====
@router.post("/cbc/generic-skills", response_model=GenericSkill, status_code=status.HTTP_201_CREATED)
async def create_generic_skill(skill_data: GenericSkillCreate) -> GenericSkill:
    """Create a generic/transferable skill."""
    global SKILL_ID_COUNTER
    skill_id = SKILL_ID_COUNTER
    SKILL_ID_COUNTER += 1
    
    new_skill = {
        "id": skill_id,
        "name": skill_data.name,
        "description": skill_data.description,
        "category": skill_data.category,
        "created_at": datetime.utcnow()
    }
    
    GENERIC_SKILLS_DB[skill_id] = new_skill
    return GenericSkill(**new_skill)


@router.get("/cbc/generic-skills", response_model=List[GenericSkill])
async def list_generic_skills(category: Optional[str] = None) -> List[GenericSkill]:
    """List generic skills."""
    skills = list(GENERIC_SKILLS_DB.values())
    
    if category:
        skills = [s for s in skills if s["category"] == category]
    
    return [GenericSkill(**s) for s in skills]


# ===== CBC COURSES =====
@router.post("/cbc/courses", response_model=CBCCourse, status_code=status.HTTP_201_CREATED)
async def create_cbc_course(course_data: CBCCourseCreate) -> CBCCourse:
    """
    Create a CBC course.
    
    **Best Practice**: Link competencies and skills before publishing
    """
    global CBC_COURSE_ID_COUNTER
    
    # Validate competencies exist
    for comp_id in course_data.competencies:
        if comp_id not in COMPETENCIES_DB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency {comp_id} not found"
            )
    
    course_id = CBC_COURSE_ID_COUNTER
    CBC_COURSE_ID_COUNTER += 1
    
    new_course = {
        "id": course_id,
        "code": course_data.code,
        "title": course_data.title,
        "description": course_data.description,
        "learning_area": course_data.learning_area,
        "cbc_level": course_data.cbc_level,
        "duration_weeks": course_data.duration_weeks,
        "instructor_id": course_data.instructor_id,
        "status": CurriculumStatus.DRAFT,
        "competencies": course_data.competencies,
        "generic_skills": course_data.generic_skills,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    CBC_COURSES_DB[course_id] = new_course
    return CBCCourse(**new_course)


@router.get("/cbc/courses", response_model=List[CBCCourse])
async def list_cbc_courses(
    skip: int = 0,
    limit: int = 10,
    cbc_level: Optional[str] = None,
    learning_area: Optional[str] = None
) -> List[CBCCourse]:
    """List CBC courses with filtering."""
    courses = list(CBC_COURSES_DB.values())
    
    if cbc_level:
        courses = [c for c in courses if c["cbc_level"] == cbc_level]
    
    if learning_area:
        courses = [c for c in courses if c["learning_area"] == learning_area]
    
    courses = courses[skip:skip + limit]
    return [CBCCourse(**c) for c in courses]


@router.get("/cbc/courses/{course_id}", response_model=CBCCourseWithDetails)
async def get_cbc_course(course_id: int) -> CBCCourseWithDetails:
    """Get CBC course with details."""
    course = CBC_COURSES_DB.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    competencies = [Competency(**COMPETENCIES_DB[cid]) for cid in course.get("competencies", []) if cid in COMPETENCIES_DB]
    learning_outcomes = [
        LearningOutcome(**o) for o in LEARNING_OUTCOMES_DB.values()
        if o["competency_id"] in course.get("competencies", [])
    ]
    generic_skills = [GenericSkill(**GENERIC_SKILLS_DB[sid]) for sid in course.get("generic_skills", []) if sid in GENERIC_SKILLS_DB]
    
    return CBCCourseWithDetails(
        **course,
        competencies=competencies,
        learning_outcomes=learning_outcomes,
        generic_skills=generic_skills
    )


@router.post("/cbc/courses/{course_id}/publish")
async def publish_cbc_course(course_id: int) -> dict:
    """Publish a CBC course."""
    course = CBC_COURSES_DB.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if not course["competencies"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course must have at least one competency"
        )
    
    course["status"] = CurriculumStatus.PUBLISHED
    return {"message": "CBC course published successfully"}


# ===== CBC CURRICULA =====
@router.post("/cbc/curricula", response_model=CBCCurriculum, status_code=status.HTTP_201_CREATED)
async def create_cbc_curriculum(curriculum_data: CBCCurriculumCreate) -> CBCCurriculum:
    """Create a CBC curriculum package."""
    global CBC_CURRICULUM_ID_COUNTER
    curriculum_id = CBC_CURRICULUM_ID_COUNTER
    CBC_CURRICULUM_ID_COUNTER += 1
    
    new_curriculum = {
        "id": curriculum_id,
        "name": curriculum_data.name,
        "description": curriculum_data.description,
        "version": curriculum_data.version,
        "cbc_level": curriculum_data.cbc_level,
        "academic_year": curriculum_data.academic_year,
        "status": CurriculumStatus.DRAFT,
        "courses": curriculum_data.courses,
        "created_at": datetime.utcnow()
    }
    
    CBC_CURRICULA_DB[curriculum_id] = new_curriculum
    return CBCCurriculum(**new_curriculum)


@router.get("/cbc/curricula", response_model=List[CBCCurriculum])
async def list_cbc_curricula(cbc_level: Optional[str] = None) -> List[CBCCurriculum]:
    """List CBC curricula."""
    curricula = list(CBC_CURRICULA_DB.values())
    
    if cbc_level:
        curricula = [c for c in curricula if c["cbc_level"] == cbc_level]
    
    return [CBCCurriculum(**c) for c in curricula]


@router.get("/cbc/curricula/{curriculum_id}", response_model=CBCCurriculumWithCourses)
async def get_cbc_curriculum(curriculum_id: int) -> CBCCurriculumWithCourses:
    """Get CBC curriculum with courses."""
    curriculum = CBC_CURRICULA_DB.get(curriculum_id)
    if not curriculum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curriculum not found"
        )
    
    courses = [CBCCourse(**CBC_COURSES_DB[cid]) for cid in curriculum.get("courses", []) if cid in CBC_COURSES_DB]
    return CBCCurriculumWithCourses(**curriculum, courses=courses)


# ===== COMPETENCY PROGRESS =====
@router.post("/cbc/competency-progress", response_model=CompetencyProgress, status_code=status.HTTP_201_CREATED)
async def record_competency_progress(progress_data: CompetencyProgressCreate) -> CompetencyProgress:
    """
    Record student competency progress.
    
    **Best Practice**: Update after each assessment
    """
    competency = COMPETENCIES_DB.get(progress_data.competency_id)
    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competency not found"
        )
    
    progress_id = len(COMPETENCY_PROGRESS_DB) + 1
    new_progress = {
        "id": progress_id,
        "student_id": progress_data.student_id,
        "competency_id": progress_data.competency_id,
        "status": progress_data.status,
        "proficiency_level": progress_data.proficiency_level,
        "last_assessed": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    COMPETENCY_PROGRESS_DB[progress_id] = new_progress
    return CompetencyProgress(**new_progress)


@router.get("/cbc/students/{student_id}/competency-progress")
async def get_student_competency_progress(student_id: int) -> dict:
    """Get all competency progress for a student."""
    progress_items = [p for p in COMPETENCY_PROGRESS_DB.values() if p["student_id"] == student_id]
    
    if not progress_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress records found for student"
        )
    
    return {
        "student_id": student_id,
        "competencies": [CompetencyProgress(**p) for p in progress_items],
        "total_achieved": sum(1 for p in progress_items if p["status"] == CompetencyStatus.ACHIEVED),
        "total_mastered": sum(1 for p in progress_items if p["status"] == CompetencyStatus.MASTERED)
    }


# ===== BRITISH SUBJECTS =====
@router.post("/british/subjects", response_model=Subject, status_code=status.HTTP_201_CREATED)
async def create_subject(subject_data: SubjectCreate) -> Subject:
    """Create a British curriculum subject."""
    global SUBJECT_ID_COUNTER
    
    # Check unique code
    if any(s["code"] == subject_data.code for s in SUBJECTS_DB.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject code {subject_data.code} already exists"
        )
    
    subject_id = SUBJECT_ID_COUNTER
    SUBJECT_ID_COUNTER += 1
    
    new_subject = {
        "id": subject_id,
        "code": subject_data.code,
        "title": subject_data.title,
        "description": subject_data.description,
        "british_level": subject_data.british_level,
        "instructor_id": subject_data.instructor_id,
        "exam_board": subject_data.exam_board,
        "created_at": datetime.utcnow()
    }
    
    SUBJECTS_DB[subject_id] = new_subject
    return Subject(**new_subject)


@router.get("/british/subjects", response_model=List[Subject])
async def list_subjects(british_level: Optional[str] = None, exam_board: Optional[str] = None) -> List[Subject]:
    """List British subjects."""
    subjects = list(SUBJECTS_DB.values())
    
    if british_level:
        subjects = [s for s in subjects if s["british_level"] == british_level]
    
    if exam_board:
        subjects = [s for s in subjects if s["exam_board"] == exam_board]
    
    return [Subject(**s) for s in subjects]


@router.get("/british/subjects/{subject_id}", response_model=Subject)
async def get_subject(subject_id: int) -> Subject:
    """Get a specific subject."""
    subject = SUBJECTS_DB.get(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return Subject(**subject)


# ===== BRITISH TOPICS =====
@router.post("/british/subjects/{subject_id}/topics", response_model=Topic, status_code=status.HTTP_201_CREATED)
async def create_topic(subject_id: int, topic_data: TopicCreate) -> Topic:
    """Create a topic for a subject."""
    subject = SUBJECTS_DB.get(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    global TOPIC_ID_COUNTER
    topic_id = TOPIC_ID_COUNTER
    TOPIC_ID_COUNTER += 1
    
    new_topic = {
        "id": topic_id,
        "subject_id": subject_id,
        "title": topic_data.title,
        "description": topic_data.description,
        "order": topic_data.order,
        "created_at": datetime.utcnow()
    }
    
    TOPICS_DB[topic_id] = new_topic
    return Topic(**new_topic)


@router.get("/british/subjects/{subject_id}/topics", response_model=List[Topic])
async def list_topics(subject_id: int) -> List[Topic]:
    """Get all topics for a subject."""
    subject = SUBJECTS_DB.get(subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    topics = sorted(
        [t for t in TOPICS_DB.values() if t["subject_id"] == subject_id],
        key=lambda x: x["order"]
    )
    return [Topic(**t) for t in topics]


# ===== BRITISH SUBTOPICS =====
@router.post("/british/topics/{topic_id}/subtopics", response_model=Subtopic, status_code=status.HTTP_201_CREATED)
async def create_subtopic(topic_id: int, subtopic_data: SubtopicCreate) -> Subtopic:
    """Create a subtopic for a topic."""
    topic = TOPICS_DB.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    global SUBTOPIC_ID_COUNTER
    subtopic_id = SUBTOPIC_ID_COUNTER
    SUBTOPIC_ID_COUNTER += 1
    
    new_subtopic = {
        "id": subtopic_id,
        "topic_id": topic_id,
        "title": subtopic_data.title,
        "learning_objectives": subtopic_data.learning_objectives,
        "order": subtopic_data.order,
        "created_at": datetime.utcnow()
    }
    
    SUBTOPICS_DB[subtopic_id] = new_subtopic
    return Subtopic(**new_subtopic)


@router.get("/british/topics/{topic_id}/subtopics", response_model=List[Subtopic])
async def list_subtopics(topic_id: int) -> List[Subtopic]:
    """Get all subtopics for a topic."""
    topic = TOPICS_DB.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    subtopics = sorted(
        [s for s in SUBTOPICS_DB.values() if s["topic_id"] == topic_id],
        key=lambda x: x["order"]
    )
    return [Subtopic(**s) for s in subtopics]


# ===== BRITISH COURSES =====
@router.post("/british/courses", response_model=BritishCourse, status_code=status.HTTP_201_CREATED)
async def create_british_course(course_data: BritishCourseCreate) -> BritishCourse:
    """Create a British curriculum course."""
    global BRITISH_COURSE_ID_COUNTER
    
    subject = SUBJECTS_DB.get(course_data.subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    course_id = BRITISH_COURSE_ID_COUNTER
    BRITISH_COURSE_ID_COUNTER += 1
    
    new_course = {
        "id": course_id,
        "code": course_data.code,
        "subject_id": course_data.subject_id,
        "title": course_data.title,
        "description": course_data.description,
        "british_level": course_data.british_level,
        "duration_weeks": course_data.duration_weeks,
        "instructor_id": course_data.instructor_id,
        "exam_board": course_data.exam_board,
        "status": CurriculumStatus.DRAFT,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    BRITISH_COURSES_DB[course_id] = new_course
    return BritishCourse(**new_course)


@router.get("/british/courses", response_model=List[BritishCourse])
async def list_british_courses(
    skip: int = 0,
    limit: int = 10,
    british_level: Optional[str] = None
) -> List[BritishCourse]:
    """List British courses."""
    courses = list(BRITISH_COURSES_DB.values())
    
    if british_level:
        courses = [c for c in courses if c["british_level"] == british_level]
    
    courses = courses[skip:skip + limit]
    return [BritishCourse(**c) for c in courses]


@router.get("/british/courses/{course_id}", response_model=BritishCourseWithDetails)
async def get_british_course(course_id: int) -> BritishCourseWithDetails:
    """Get British course with details."""
    course = BRITISH_COURSES_DB.get(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    subject = Subject(**SUBJECTS_DB[course["subject_id"]]) if course["subject_id"] in SUBJECTS_DB else None
    topics = [Topic(**t) for t in TOPICS_DB.values() if t["subject_id"] == course["subject_id"]]
    
    return BritishCourseWithDetails(**course, subject=subject, topics=topics)


# ===== BRITISH CURRICULA =====
@router.post("/british/curricula", response_model=BritishCurriculum, status_code=status.HTTP_201_CREATED)
async def create_british_curriculum(curriculum_data: BritishCurriculumCreate) -> BritishCurriculum:
    """Create a British curriculum package."""
    curriculum_id = len(BRITISH_CURRICULA_DB) + 1
    
    new_curriculum = {
        "id": curriculum_id,
        "name": curriculum_data.name,
        "description": curriculum_data.description,
        "version": curriculum_data.version,
        "british_level": curriculum_data.british_level,
        "exam_board": curriculum_data.exam_board,
        "academic_year": curriculum_data.academic_year,
        "status": CurriculumStatus.DRAFT,
        "subjects": curriculum_data.subjects,
        "created_at": datetime.utcnow()
    }
    
    BRITISH_CURRICULA_DB[curriculum_id] = new_curriculum
    return BritishCurriculum(**new_curriculum)


@router.get("/british/curricula", response_model=List[BritishCurriculum])
async def list_british_curricula(british_level: Optional[str] = None) -> List[BritishCurriculum]:
    """List British curricula."""
    curricula = list(BRITISH_CURRICULA_DB.values())
    
    if british_level:
        curricula = [c for c in curricula if c["british_level"] == british_level]
    
    return [BritishCurriculum(**c) for c in curricula]


@router.get("/british/curricula/{curriculum_id}", response_model=BritishCurriculumWithSubjects)
async def get_british_curriculum(curriculum_id: int) -> BritishCurriculumWithSubjects:
    """Get British curriculum with subjects."""
    curriculum = BRITISH_CURRICULA_DB.get(curriculum_id)
    if not curriculum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curriculum not found"
        )
    
    subjects = [Subject(**SUBJECTS_DB[sid]) for sid in curriculum.get("subjects", []) if sid in SUBJECTS_DB]
    return BritishCurriculumWithSubjects(**curriculum, subjects=subjects)


# ===== ASSESSMENTS (SHARED) =====
@router.post("/assessments", response_model=Assessment, status_code=status.HTTP_201_CREATED)
async def create_assessment(assessment_data: AssessmentCreate) -> Assessment:
    """Create an assessment for CBC or British courses."""
    global ASSESSMENT_ID_COUNTER
    assessment_id = ASSESSMENT_ID_COUNTER
    ASSESSMENT_ID_COUNTER += 1
    
    new_assessment = {
        "id": assessment_id,
        "title": assessment_data.title,
        "description": assessment_data.description,
        "assessment_type": assessment_data.assessment_type,
        "max_score": assessment_data.max_score,
        "duration_minutes": assessment_data.duration_minutes,
        "cbc_course_id": assessment_data.cbc_course_id,
        "british_course_id": assessment_data.british_course_id,
        "created_at": datetime.utcnow()
    }
    
    ASSESSMENTS_DB[assessment_id] = new_assessment
    return Assessment(**new_assessment)


@router.get("/assessments", response_model=List[Assessment])
async def list_assessments(
    skip: int = 0,
    limit: int = 10,
    assessment_type: Optional[str] = None
) -> List[Assessment]:
    """List assessments."""
    assessments = list(ASSESSMENTS_DB.values())
    
    if assessment_type:
        assessments = [a for a in assessments if a["assessment_type"] == assessment_type]
    
    assessments = assessments[skip:skip + limit]
    return [Assessment(**a) for a in assessments]


@router.get("/assessments/{assessment_id}", response_model=Assessment)
async def get_assessment(assessment_id: int) -> Assessment:
    """Get a specific assessment."""
    assessment = ASSESSMENTS_DB.get(assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    return Assessment(**assessment)


# ===== STUDENT ASSESSMENTS =====
@router.post("/assessments/{assessment_id}/submit", response_model=StudentAssessment, status_code=status.HTTP_201_CREATED)
async def submit_assessment(assessment_id: int, submission_data: StudentAssessmentCreate) -> StudentAssessment:
    """Submit an assessment and record score."""
    assessment = ASSESSMENTS_DB.get(assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Validate score
    if not 0 <= submission_data.score <= assessment["max_score"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Score must be between 0 and max_score"
        )
    
    assessment_id_record = len(STUDENT_ASSESSMENTS_DB) + 1
    
    # Determine grade based on percentage
    percentage = (submission_data.score / assessment["max_score"]) * 100
    if assessment["cbc_course_id"]:
        grade = get_cbc_grade(percentage)
    else:
        grade = get_british_grade(percentage)
    
    new_record = {
        "id": assessment_id_record,
        "student_id": submission_data.student_id,
        "assessment_id": assessment_id,
        "score": submission_data.score,
        "grade": grade,
        "competencies_achieved": submission_data.competencies_achieved,
        "comments": submission_data.comments,
        "submitted_at": submission_data.submitted_at,
        "created_at": datetime.utcnow()
    }
    
    STUDENT_ASSESSMENTS_DB[assessment_id_record] = new_record
    return StudentAssessment(**new_record)


@router.get("/students/{student_id}/assessments")
async def get_student_assessments(student_id: int) -> dict:
    """Get all assessments for a student."""
    assessments = [a for a in STUDENT_ASSESSMENTS_DB.values() if a["student_id"] == student_id]
    
    if not assessments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessments found for student"
        )
    
    return {
        "student_id": student_id,
        "assessments": [StudentAssessment(**a) for a in assessments],
        "average_score": sum(a["score"] for a in assessments) / len(assessments) if assessments else 0
    }


# ===== LEARNING RESOURCES =====
@router.post("/resources", response_model=LearningResource, status_code=status.HTTP_201_CREATED)
async def create_resource(resource_data: LearningResourceCreate) -> LearningResource:
    """Create a learning resource."""
    resource_id = len(RESOURCES_DB) + 1
    
    new_resource = {
        "id": resource_id,
        "title": resource_data.title,
        "description": resource_data.description,
        "resource_type": resource_data.resource_type,
        "url": resource_data.url,
        "file_path": resource_data.file_path,
        "cbc_course_id": resource_data.cbc_course_id,
        "british_course_id": resource_data.british_course_id,
        "created_at": datetime.utcnow()
    }
    
    RESOURCES_DB[resource_id] = new_resource
    return LearningResource(**new_resource)


@router.get("/resources", response_model=List[LearningResource])
async def list_resources(skip: int = 0, limit: int = 10) -> List[LearningResource]:
    """List all learning resources."""
    resources = list(RESOURCES_DB.values())[skip:skip + limit]
    return [LearningResource(**r) for r in resources]


@router.get("/resources/cbc-courses/{course_id}", response_model=List[LearningResource])
async def get_cbc_course_resources(course_id: int) -> List[LearningResource]:
    """Get resources for a CBC course."""
    resources = [r for r in RESOURCES_DB.values() if r["cbc_course_id"] == course_id]
    return [LearningResource(**r) for r in resources]


@router.get("/resources/british-courses/{course_id}", response_model=List[LearningResource])
async def get_british_course_resources(course_id: int) -> List[LearningResource]:
    """Get resources for a British course."""
    resources = [r for r in RESOURCES_DB.values() if r["british_course_id"] == course_id]
    return [LearningResource(**r) for r in resources]


# ===== HELPER FUNCTIONS =====
def get_cbc_grade(percentage: float) -> str:
    """Convert percentage to CBC grade."""
    if percentage >= 90:
        return "E"  # Exceeds Expectations
    elif percentage >= 70:
        return "M"  # Meets Expectations
    elif percentage >= 50:
        return "A"  # Approaches Expectations
    else:
        return "B"  # Below Expectations


def get_british_grade(percentage: float) -> str:
    """Convert percentage to British grade."""
    if percentage >= 90:
        return "A*"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "F"
