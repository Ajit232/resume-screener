from django.db import models
from django.contrib.auth.models import User


class JobDescription(models.Model):

    EDUCATION_CHOICES = [
        ("", "Not specified"),
        ("any", "Any"),
        ("diploma", "Diploma"),
        ("bachelor", "Bachelor Degree"),
        ("master", "Master Degree"),
        ("phd", "PhD"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_descriptions")
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default="")
    raw_text = models.TextField()
    file = models.FileField(upload_to="job_descriptions/", blank=True, null=True)
    parsed_skills = models.JSONField(default=list)
    parsed_keywords = models.JSONField(default=list)
    experience_required = models.CharField(max_length=100, blank=True, default="")
    education_required = models.CharField(max_length=20, blank=True, default="", choices=EDUCATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job Description"
        verbose_name_plural = "Job Descriptions"

    def __str__(self):
        company_str = f" @ {self.company}" if self.company else ""
        return f"{self.title}{company_str} ({self.user.username})"

    def skill_count(self):
        return len(self.parsed_skills)

    def keyword_count(self):
        return len(self.parsed_keywords)
