from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import make_engine
from app.research_models import Course, Enrollment, ResearchBase, Student, Teacher


def test_student_course_teacher_mapping():
    engine = make_engine("sqlite://", echo=False)
    ResearchBase.metadata.create_all(engine)
    with Session(engine) as s:
        teacher = Teacher(full_name="O'qituvchi 1")
        c1, c2 = Course(title="Kurs 1", teacher=teacher), Course(title="Kurs 2", teacher=teacher)
        st1, st2 = Student(full_name="Talaba 1"), Student(full_name="Talaba 2")
        s.add_all([
            Enrollment(student=st1, course=c1, grade=5),
            Enrollment(student=st1, course=c2, grade=4),
            Enrollment(student=st2, course=c1),
        ])
        s.commit()
        assert len(teacher.courses) == 2  # One-to-Many
        assert {e.course.title for e in st1.enrollments} == {"Kurs 1", "Kurs 2"}  # Many-to-Many
        assert len(c1.enrollments) == 2
        assert s.scalars(select(Enrollment).where(Enrollment.grade.is_(None))).one().student is st2
