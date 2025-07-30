import pytest
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field


class SellerInfoResponseStructure(BaseModel):
    name: str
    sid: str
    trademark: str = Field(..., alias="tradeMark")
    model_config = ConfigDict(extra="forbid")


@pytest.mark.asyncio
async def test_get_seller_info_structure(wb_client):
    result = await wb_client.get_seller_info()
    SellerInfoResponseStructure.model_validate(result)


@pytest.mark.asyncio
async def test_get_seller_info(wb_client, load_config, load_testdata):
    result = await wb_client.get_seller_info()
    expected = load_testdata["wb"]["expected_seller_info"]
    assert result == expected
