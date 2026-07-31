"""
文档模型 — Document & DocumentTemplate

Document: 文档内容，可关联项目，支持文件上传、标签、引用检查
DocumentTemplate: 文档模板，用于快速创建同类别文档
"""

from tortoise import fields

from models.basic_model import BaseModel


class Document(BaseModel):
    """文档 — 项目中的文档内容"""

    project = fields.ForeignKeyField(
        "models.Project", related_name="documents", null=True,
        description="所属项目",
    )
    title = fields.CharField(max_length=255, description="文档标题")
    content = fields.TextField(default="", description="文档内容")
    file_path = fields.CharField(max_length=1024, default="", description="上传文件路径")
    mime_type = fields.CharField(max_length=128, default="", description="MIME 类型")
    tags = fields.JSONField(default=list, description="标签列表")

    class Meta:
        table = "documents"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"<Document {self.id}: {self.title}>"


class DocumentTemplate(BaseModel):
    """文档模板 — 预定义文档结构"""

    name = fields.CharField(max_length=255, description="模板名称")
    description = fields.TextField(default="", description="模板描述")
    category = fields.CharField(max_length=64, default="general", description="模板分类")
    content = fields.TextField(default="", description="模板内容")

    class Meta:
        table = "document_templates"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"<DocumentTemplate {self.id}: {self.name}>"
