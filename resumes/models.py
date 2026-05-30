from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=255)
    raw_text = models.TextField(blank=True, default="")
    file = models.FileField(upload_to="resumes/", blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_optimized = models.BooleanField(default=False)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_versions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        tag = " [optimised]" if self.is_optimized else ""
        return f"{self.title} v{self.version}{tag} ({self.user.username})"

    def word_count(self):
        if self.raw_text:
            return len(self.raw_text.split())
        return 0

    def get_all_versions(self):
        root = self
        while root.parent is not None:
            root = root.parent
        versions = [root]
        versions.extend(list(root.child_versions.order_by("version")))
        return versions
