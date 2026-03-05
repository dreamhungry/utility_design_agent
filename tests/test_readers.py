"""数据源读取测试"""

import pytest

from utility_design_agent.models import NPCData
from utility_design_agent.readers import DictReader, create_reader


class TestDictReader:
    @pytest.mark.asyncio
    async def test_read_basic(self):
        reader = DictReader()
        data = [
            {
                "name": "哥布林",
                "personality_tags": ["胆小", "贪婪"],
                "behavior_preferences": ["逃跑", "拾取"],
                "design_intent": "测试意图",
            }
        ]
        npcs = await reader.read(data=data)
        assert len(npcs) == 1
        assert npcs[0].name == "哥布林"
        assert npcs[0].personality_tags == ["胆小", "贪婪"]

    @pytest.mark.asyncio
    async def test_read_empty(self):
        reader = DictReader()
        npcs = await reader.read(data=[])
        assert npcs == []

    @pytest.mark.asyncio
    async def test_read_none(self):
        reader = DictReader()
        npcs = await reader.read(data=None)
        assert npcs == []

    @pytest.mark.asyncio
    async def test_read_minimal(self):
        reader = DictReader()
        data = [{"name": "简单NPC"}]
        npcs = await reader.read(data=data)
        assert npcs[0].name == "简单NPC"
        assert npcs[0].personality_tags == []


class TestCreateReader:
    def test_create_dict_reader(self):
        reader = create_reader("dict")
        assert isinstance(reader, DictReader)

    def test_invalid_source_type(self):
        with pytest.raises(ValueError, match="不支持的数据源类型"):
            create_reader("invalid")


class TestLocalReader:
    @pytest.mark.asyncio
    async def test_missing_path_raises(self):
        from utility_design_agent.readers import LocalReader

        reader = LocalReader()
        with pytest.raises(ValueError, match="必须提供 path 参数"):
            await reader.read()

    @pytest.mark.asyncio
    async def test_nonexistent_file_raises(self):
        from utility_design_agent.readers import LocalReader

        reader = LocalReader()
        with pytest.raises(FileNotFoundError):
            await reader.read(path="/nonexistent/file.xlsx")
