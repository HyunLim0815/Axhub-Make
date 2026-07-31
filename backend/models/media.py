"""
媒体文件模型 — MediaFile

存储上传的媒体资源（图片、视频、文档等），
支持按项目、文件夹分类管理。
"""

from tortoise import fields

from models.basic_model import BaseModel


class MediaFile(BaseModel):
    """媒体文件 — 上传资源的元数据记录"""

    project = fields.ForeignKeyField(
        "models.Project",
        null=True,
        on_delete=fields.SET_NULL,
        description="所属项目（可选）",
    )
    filename = fields.CharField(max_length=255, description="原始文件名")
    filepath = fields.CharField(max_length=1024, description="存储路径")
    mime_type = fields.CharField(max_length=128, default="", description="MIME 类型")
    size = fields.IntField(default=0, description="文件大小（字节）")
    folder = fields.CharField(max_length=512, default="", description="分类文件夹")

    class Meta:
        table = "media_files"
        ordering = ["-id"]
