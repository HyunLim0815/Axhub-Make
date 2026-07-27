"""标注 API 集成测试"""

import pytest


class TestAnnotationAPI:
    """标注 CRUD + 版本 API 测试"""

    @pytest.mark.asyncio
    async def test_create_annotation(self, client):
        # 先创建原型
        resp = await client.post("/v1/prototypes/", json={"name": "test"})
        assert resp.status_code == 201
        proto_id = resp.json()["data"]["id"]

        # 创建标注
        resp = await client.post("/v1/annotations/", json={
            "prototype_id": proto_id,
            "title": "测试标注",
            "color": "#ff0000",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["title"] == "测试标注"
        assert data["color"] == "#ff0000"

    @pytest.mark.asyncio
    async def test_list_annotations(self, client):
        resp = await client.get("/v1/annotations/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "data" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, client):
        resp = await client.get("/v1/annotations/99999")
        assert resp.status_code == 200
        assert resp.json()["code"] == 404


class TestKnowledgeAPI:
    """知识库 API 测试"""

    @pytest.mark.asyncio
    async def test_create_entry(self, client):
        resp = await client.post("/v1/knowledge/", json={
            "type": "term",
            "title": "API网关",
            "content": "统一的API入口服务",
            "tags": ["backend"],
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["title"] == "API网关"

    @pytest.mark.asyncio
    async def test_search(self, client):
        resp = await client.get("/v1/knowledge/?q=网关")
        assert resp.status_code == 200
        assert len(resp.json()["data"]["data"]) >= 1


class TestPublishAPI:
    """发布 API 测试"""

    @pytest.mark.asyncio
    async def test_get_channels(self, client):
        resp = await client.get("/v1/publish/channels")
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)

    @pytest.mark.asyncio
    async def test_deploy(self, client):
        # 先获取通道
        resp = await client.get("/v1/publish/channels")
        channels = resp.json()["data"]
        if not channels:
            return  # skip if no channels

        resp = await client.post(f"/v1/publish/channels/{channels[0]['id']}/deploy")
        assert resp.status_code == 201
        assert resp.json()["data"]["version"] == 1
