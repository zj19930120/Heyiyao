# -*- coding: utf-8 -*-
"""
生成纯净的四川省地图
包含各市/州边界，用单色系区分，突出显示泸州市
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import json
import os

# 设置中文字体（防止乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def download_sichuan_geojson():
    """
    下载四川省市级行政区划GeoJSON数据
    """
    # 使用阿里云的四川省地图数据（包含市/州边界）
    # 510000 是四川省的行政区划代码
    url = "https://geo.datav.aliyun.com/areas_v3/bound/510000_full.json"

    print("正在下载四川省地图数据...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print("✅ 四川省地图数据下载成功")
        return data
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print("将使用备用方案...")
        return None

def create_clean_sichuan_map(output_path, width=2400, height=1800, dpi=150):
    """
    创建纯净的四川省地图，包含各市/州边界，突出显示泸州市

    参数：
    - output_path: 输出文件路径
    - width: 图片宽度（像素）
    - height: 图片高度（像素）
    - dpi: 分辨率
    """

    # 下载GeoJSON数据
    geojson_data = download_sichuan_geojson()

    if not geojson_data:
        print("❌ 无法获取地图数据")
        return False

    # 计算图片尺寸（英寸）
    fig_width = width / dpi
    fig_height = height / dpi

    # 创建图形
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    # 设置背景色为深色科技风格
    fig.patch.set_facecolor('#0f172a')  # 深蓝色背景
    ax.set_facecolor('#0f172a')  # 深蓝色背景

    # 定义单色系颜色方案（蓝色系 - 适配深色背景）
    # matplotlib使用RGB元组格式 (R/255, G/255, B/255)
    city_colors = [
        (33/255, 150/255, 243/255), (25/255, 118/255, 210/255), (21/255, 101/255, 192/255),
        (13/255, 71/255, 161/255), (66/255, 165/255, 245/255), (100/255, 181/255, 246/255),
        (144/255, 202/255, 249/255), (187/255, 222/255, 251/255), (30/255, 136/255, 229/255),
        (25/255, 118/255, 210/255), (21/255, 101/255, 192/255), (13/255, 71/255, 161/255),
        (33/255, 150/255, 243/255), (66/255, 165/255, 245/255), (100/255, 181/255, 246/255),
        (144/255, 202/255, 249/255), (187/255, 222/255, 251/255), (30/255, 136/255, 229/255),
        (25/255, 118/255, 210/255), (21/255, 101/255, 192/255), (13/255, 71/255, 161/255)
    ]

    # 泸州市高亮颜色（红色突出）
    luzhou_color = (255/255, 82/255, 82/255)  # #ff5252
    luzhou_edge_color = (211/255, 47/255, 47/255)  # #d32f2f

    # 其他城市边界颜色（亮蓝色）
    normal_edge_color = (0/255, 212/255, 255/255)  # #00d4ff

    # 遍历所有市/州
    color_index = 0
    city_count = 0
    for feature in geojson_data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        city_name = properties.get('name', '')

        # 判断是否为泸州市
        is_luzhou = '泸州' in city_name

        # 选择颜色（深色背景下的配色）
        if is_luzhou:
            fill_color = luzhou_color
            edge_color = luzhou_edge_color
            linewidth = 3.0
            alpha = 0.6  # 半透明
        else:
            fill_color = city_colors[color_index % len(city_colors)]
            edge_color = normal_edge_color  # 亮蓝色边界
            linewidth = 2.0
            alpha = 0.4  # 半透明
            color_index += 1

        # 绘制市/州边界
        if geometry['type'] == 'Polygon':
            for coords in geometry['coordinates']:
                lons = [point[0] for point in coords]
                lats = [point[1] for point in coords]
                ax.fill(lons, lats, color=fill_color, edgecolor=edge_color,
                       linewidth=linewidth, alpha=alpha)
        elif geometry['type'] == 'MultiPolygon':
            for polygon in geometry['coordinates']:
                for coords in polygon:
                    lons = [point[0] for point in coords]
                    lats = [point[1] for point in coords]
                    ax.fill(lons, lats, color=fill_color, edgecolor=edge_color,
                           linewidth=linewidth, alpha=alpha)

        city_count += 1

    # 设置坐标轴范围（四川省范围）
    ax.set_xlim(97, 110)
    ax.set_ylim(26, 35)

    # 隐藏坐标轴
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # 保持纵横比
    ax.set_aspect('equal')

    # 去除边距
    plt.tight_layout(pad=0.5)

    # 保存图片
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    print(f"✅ 纯净地图已生成: {output_path}")
    print(f"   尺寸: {width}x{height} 像素")
    print(f"   分辨率: {dpi} DPI")
    print(f"   市/州数量: {city_count}")

    return True

if __name__ == "__main__":
    print("=" * 70)
    print("  四川省地图生成工具 - 包含各市/州边界，突出显示泸州市")
    print("=" * 70)
    print()

    # 生成地图到两个位置
    output_paths = [
        "基础知识/地图.png",
        "基础知识_html/地图/images/地图.png"
    ]

    success_count = 0
    for output_path in output_paths:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 生成地图
        print(f"正在生成: {output_path}")
        if create_clean_sichuan_map(output_path, width=2400, height=1800, dpi=150):
            success_count += 1
        print()

    if success_count > 0:
        print("=" * 70)
        print("✅ 地图文件已生成完成！")
        print("=" * 70)
        print()
        print("📝 生成的文件：")
        for path in output_paths:
            if os.path.exists(path):
                size = os.path.getsize(path) / 1024  # KB
                print(f"   ✓ {path} ({size:.1f} KB)")
        print()
        print("🎨 地图特点：")
        print("   • 只显示四川省区域")
        print("   • 包含所有市/州边界（21个）")
        print("   • 单色系（蓝色系）区分各市/州")
        print("   • 泸州市用红色突出显示")
        print("   • 无文字标注，纯净简洁")
        print()
        print("💡 提示：请在浏览器中刷新页面查看新地图")
    else:
        print("❌ 地图生成失败，请检查网络连接或稍后重试")

