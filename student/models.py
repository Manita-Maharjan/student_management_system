
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone



class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    dob = models.DateField()
    metadata = models.ManyToManyField("Metadata", related_name="students", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    


course_code_validator = RegexValidator(
    regex=r'^[A-Z0-9]+$',
    message="Course code must be capital letters and numbers only."
)

class Course(models.Model):
    name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=20, unique=True, validators=[course_code_validator])
    description = models.TextField(blank=True)
    metadata = models.ManyToManyField("Metadata", related_name="courses", blank=True)

    def __str__(self):
        return f"{self.name}-{self.course_code} "
    
    def clean(self):
        self.course_code = self.course_code.upper()


class Instructor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    courses = models.ManyToManyField(Course, related_name="instructors", blank=True)
    metadata = models.ManyToManyField("Metadata", related_name="instructors", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    metadata = models.ManyToManyField("Metadata", related_name="enrollments", blank=True)

    class Meta:
        unique_together = ("student", "course")
        indexes = [
            models.Index(fields=["student", "course"]),
        ]

    def __str__(self):
        return f"{self.student} in {self.course}"


class Metadata(models.Model):
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}={self.value}"
