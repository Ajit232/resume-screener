from django.db import models
from django.contrib.auth.models import User
from resumes.models import Resume
from jobs.models import JobDescription


class AnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="analyses")
    skill_match_score = models.FloatField(default=0.0)
    keyword_match_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    education_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Analysis Result"
        verbose_name_plural = "Analysis Results"

    def __str__(self):
        return f"Analysis #{self.pk} | Score: {self.final_score:.1f}"

    def get_label(self):
        if self.final_score >= 80:
            return "Strong Match"
        elif self.final_score >= 60:
            return "Good Match"
        elif self.final_score >= 40:
            return "Partial Match"
        return "Low Match"

    def get_label_color(self):
        if self.final_score >= 80:
            return "success"
        elif self.final_score >= 60:
            return "info"
        elif self.final_score >= 40:
            return "warning"
        return "danger"

    def get_score_class(self):
        if self.final_score >= 80:
            return "strong"
        elif self.final_score >= 60:
            return "good"
        elif self.final_score >= 40:
            return "partial"
        return "low"
