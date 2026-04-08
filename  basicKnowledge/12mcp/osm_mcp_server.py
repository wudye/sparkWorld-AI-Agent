#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OpenStreetMap Tools")

# OpenStreetMap Nominatim API 基础 URL
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"


@mcp.tool()
async def geocode(address: str) -> str:
    """地理编码：将地址转换为经纬度坐标

    Args:
        address: 要查询的地址，例如 "北京市天安门广场" 或 "Eiffel Tower, Paris"

    Returns:
        包含经纬度坐标和地址信息的JSON字符串
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "MCP-OpenStreetMap/1.0"
            }

            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                return json.dumps({
                    "error": "未找到匹配的地址",
                    "query": address
                }, ensure_ascii=False)

            result = data[0]
            return json.dumps({
                "latitude": float(result.get("lat", 0)),
                "longitude": float(result.get("lon", 0)),
                "display_name": result.get("display_name", ""),
                "address": result.get("address", {}),
                "type": result.get("type", "")
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"地理编码失败: {str(e)}",
            "query": address
        }, ensure_ascii=False)


@mcp.tool()
async def reverse_geocode(latitude: float, longitude: float) -> str:
    """逆地理编码：将经纬度坐标转换为地址

    Args:
        latitude: 纬度，范围 -90 到 90
        longitude: 经度，范围 -180 到 180

    Returns:
        包含地址信息的JSON字符串
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "MCP-OpenStreetMap/1.0"
            }

            response = await client.get(
                f"{NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            return json.dumps({
                "latitude": latitude,
                "longitude": longitude,
                "display_name": data.get("display_name", ""),
                "address": data.get("address", {}),
                "type": data.get("type", "")
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"逆地理编码失败: {str(e)}",
            "coordinates": {"lat": latitude, "lon": longitude}
        }, ensure_ascii=False)


@mcp.tool()
async def search_nearby(query: str, latitude: float, longitude: float, radius: int = 1000) -> str:
    """搜索指定位置附近的地点

    Args:
        query: 搜索关键词，例如 "restaurant", "cafe", "hotel"
        latitude: 中心点的纬度
        longitude: 中心点的经度
        radius: 搜索半径（米），默认1000米

    Returns:
        包含附近地点列表的JSON字符串
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 构建边界框
            # 简化计算：使用半径计算边界
            lat_delta = radius / 111000  # 1度纬度约111公里
            lon_delta = radius / (111000 * abs(latitude) if latitude != 0 else 111000)

            bbox = f"{longitude - lon_delta},{latitude - lat_delta},{longitude + lon_delta},{latitude + lat_delta}"

            params = {
                "q": query,
                "format": "json",
                "limit": 10,
                "bounded": 1,
                "viewbox": bbox,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "MCP-OpenStreetMap/1.0"
            }

            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data[:10]:  # 限制返回10个结果
                # 计算距离（简化版，使用Haversine公式）
                distance = calculate_distance(latitude, longitude, float(item.get("lat", 0)), float(item.get("lon", 0)))

                if distance <= radius:
                    results.append({
                        "name": item.get("display_name", ""),
                        "address": item.get("address", {}),
                        "latitude": float(item.get("lat", 0)),
                        "longitude": float(item.get("lon", 0)),
                        "type": item.get("type", ""),
                        "distance_meters": round(distance, 2)
                    })

            return json.dumps({
                "query": query,
                "center": {"lat": latitude, "lon": longitude},
                "radius_meters": radius,
                "results": results,
                "total": len(results)
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"搜索附近地点失败: {str(e)}",
            "query": query
        }, ensure_ascii=False)


@mcp.tool()
async def get_address_details(address: str) -> str:
    """获取地址的详细信息，包括行政区划

    Args:
        address: 要查询的地址

    Returns:
        包含详细地址信息的JSON字符串
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1,
                "extratags": 1,
                "namedetails": 1
            }
            headers = {
                "User-Agent": "MCP-OpenStreetMap/1.0"
            }

            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                return json.dumps({
                    "error": "未找到匹配的地址",
                    "query": address
                }, ensure_ascii=False)

            result = data[0]
            address_details = result.get("address", {})

            return json.dumps({
                "display_name": result.get("display_name", ""),
                "type": result.get("type", ""),
                "country": address_details.get("country", ""),
                "state": address_details.get("state", ""),
                "city": address_details.get("city") or address_details.get("town") or address_details.get("village",
                                                                                                          ""),
                "postcode": address_details.get("postcode", ""),
                "street": address_details.get("road", ""),
                "house_number": address_details.get("house_number", ""),
                "latitude": float(result.get("lat", 0)),
                "longitude": float(result.get("lon", 0))
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"获取地址详情失败: {str(e)}",
            "query": address
        }, ensure_ascii=False)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """使用Haversine公式计算两点之间的距离（米）"""
    from math import radians, sin, cos, sqrt, asin

    # 将角度转换为弧度
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # 地球半径（米）
    r = 6371000
    return c * r


if __name__ == "__main__":
    mcp.run(transport="stdio")
