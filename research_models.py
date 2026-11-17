"""Mini-tadqiqot: Talaba - Kurs - O'qituvchi domeni uchun ER diagrammaning ORM xaritalanishi.

  Teacher 1 --- N Course          (One-to-Many)
  Student N --- M Course          (Many-to-Many, Enrollment assotsiatsiya ob'ekti orqali)

Alohida Base ishlatilgan, shuning uchun asosiy loyiha migratsiyalariga ta'sir qilmaydi.
"""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class ResearchBase(DeclarativeBase):
    pass


class Teacher(ResearchBase):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))

    courses: Mapped[list[Course]] = relationship(back_populates="teacher")


class Course(ResearchBase):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))

    teacher: Mapped[Teacher] = relationship(back_populates="courses")
    enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class Student(ResearchBase):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))

    enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Enrollment(ResearchBase):
    """Talaba va kurs orasidagi Many-to-Many aloqa; qo'shimcha maydon (baho) bor."""

    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    grade: Mapped[int | None]

    student: Mapped[Student] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")
