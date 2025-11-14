#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转HTML转换器
将PDF文件转换为高质量HTML页面（每页转为高清图片）
"""

import os
import json
import fitz  # PyMuPDF
from PIL import Image
import io

class PDFToHTMLConverter:
    def __init__(self, pdf_folder="产业图谱", output_folder="产业图谱_html", dpi=200,
                 image_folder="基础知识", image_output_folder="基础知识_html"):
        """
        初始化转换器

        Args:
            pdf_folder: PDF文件所在文件夹
            output_folder: 输出HTML文件的文件夹
            dpi: 图片分辨率（默认200 DPI，平衡质量和文件大小）
            image_folder: 图片文件所在文件夹
            image_output_folder: 图片HTML输出文件夹
        """
        self.pdf_folder = pdf_folder
        self.output_folder = output_folder
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF默认72 DPI
        self.image_folder = image_folder
        self.image_output_folder = image_output_folder
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
        
    def convert_pdf_to_images(self, pdf_path, output_dir):
        """
        将PDF的每一页转换为PNG图片
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 图片输出目录
            
        Returns:
            page_count: 总页数
        """
        print(f"  正在转换PDF: {os.path.basename(pdf_path)}")
        
        # 创建图片输出目录
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # 打开PDF
        pdf_document = fitz.open(pdf_path)
        page_count = pdf_document.page_count
        
        print(f"  总页数: {page_count}")
        
        # 转换每一页
        for page_num in range(page_count):
            page = pdf_document[page_num]
            
            # 设置缩放矩阵以提高分辨率
            mat = fitz.Matrix(self.zoom, self.zoom)
            
            # 渲染页面为图片
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # 转换为PIL Image进行优化
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # 保存图片
            img_path = os.path.join(images_dir, f"page_{page_num + 1:03d}.png")
            img.save(img_path, "PNG", optimize=True)
            
            print(f"    ✓ 第 {page_num + 1}/{page_count} 页已转换")
        
        pdf_document.close()
        print(f"  ✅ PDF转换完成！")
        
        return page_count
    
    def generate_html(self, output_dir, title, page_count, pdf_filename):
        """
        生成HTML查看器页面
        
        Args:
            output_dir: 输出目录
            title: 文档标题
            page_count: 总页数
            pdf_filename: 原始PDF文件名
        """
        print(f"  正在生成HTML页面...")
        
        html_content = self.get_html_template(title, page_count, pdf_filename)
        
        # 保存HTML文件
        html_path = os.path.join(output_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"  ✅ HTML页面已生成: {html_path}")
    
    def save_metadata(self, output_dir, title, page_count, pdf_filename):
        """
        保存文档元数据
        
        Args:
            output_dir: 输出目录
            title: 文档标题
            page_count: 总页数
            pdf_filename: 原始PDF文件名
        """
        metadata = {
            "title": title,
            "page_count": page_count,
            "pdf_filename": pdf_filename,
            "dpi": self.dpi
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 元数据已保存")
    
    def get_html_template(self, title, page_count, pdf_filename):
        """
        获取HTML模板
        """
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - HTML版本</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            background: #1a1a1a;
            overflow: hidden;
        }}

        .viewer-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #1a1a1a;
        }}

        /* 顶部工具栏 */
        .toolbar {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            z-index: 100;
        }}

        .toolbar-left {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .toolbar-title {{
            color: #fff;
            font-size: 18px;
            font-weight: 600;
        }}

        .toolbar-right {{
            display: flex;
            gap: 10px;
        }}

        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        /* 主内容区 */
        .content-area {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        /* 页面显示区 */
        .page-display {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: auto;
            padding: 20px;
            position: relative;
        }}

        .page-image {{
            max-width: 100%;
            max-height: 100%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            transition: transform 0.3s;
        }}

        /* 底部控制栏 */
        .controls {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 20px 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
        }}

        .page-nav {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .nav-btn {{
            width: 45px;
            height: 45px;
            border: none;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 20px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .nav-btn:hover:not(:disabled) {{
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
        }}

        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}

        .page-info {{
            color: #fff;
            font-size: 16px;
            font-weight: 600;
            min-width: 120px;
            text-align: center;
        }}

        .page-input {{
            width: 60px;
            padding: 8px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-align: center;
            font-size: 14px;
        }}

        .zoom-controls {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .zoom-btn {{
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .zoom-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        .zoom-level {{
            color: #fff;
            font-size: 14px;
            min-width: 60px;
            text-align: center;
        }}

        /* 加载动画 */
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
            font-size: 18px;
        }}

        .spinner {{
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top-color: #4facfe;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .toolbar {{
                padding: 10px 15px;
            }}

            .toolbar-title {{
                font-size: 14px;
            }}

            .btn {{
                padding: 8px 12px;
                font-size: 12px;
            }}

            .controls {{
                padding: 15px;
                flex-wrap: wrap;
            }}

            .page-info {{
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="viewer-container">
        <!-- 顶部工具栏 -->
        <div class="toolbar">
            <div class="toolbar-left">
                <button class="btn btn-primary" onclick="goBackHome()">
                    <span>←</span>
                    <span>返回主页</span>
                </button>
                <div class="toolbar-title">{title}</div>
            </div>
            <div class="toolbar-right">
                <button class="btn btn-secondary" onclick="downloadPDF()">
                    <span>📥</span>
                    <span>下载PDF</span>
                </button>
                <button class="btn btn-secondary" onclick="toggleFullscreen()">
                    <span>⛶</span>
                    <span>全屏</span>
                </button>
            </div>
        </div>

        <!-- 主内容区 -->
        <div class="content-area">
            <div class="page-display" id="pageDisplay">
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div>加载中...</div>
                </div>
                <img id="pageImage" class="page-image" style="display: none;" alt="文档页面">
            </div>
        </div>

        <!-- 底部控制栏 -->
        <div class="controls">
            <div class="page-nav">
                <button class="nav-btn" id="prevBtn" onclick="prevPage()">←</button>
                <div class="page-info">
                    <input type="number" id="pageInput" class="page-input" min="1" max="{page_count}" value="1" onchange="jumpToPage()">
                    <span> / {page_count}</span>
                </div>
                <button class="nav-btn" id="nextBtn" onclick="nextPage()">→</button>
            </div>

            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut()">−</button>
                <div class="zoom-level" id="zoomLevel">100%</div>
                <button class="zoom-btn" onclick="zoomIn()">+</button>
                <button class="zoom-btn" onclick="resetZoom()" title="适应屏幕">⊡</button>
            </div>
        </div>
    </div>

    <script>
        // 全局变量
        let currentPage = 1;
        const totalPages = {page_count};
        let zoomLevel = 1.0;
        const pdfFilename = "{pdf_filename}";

        // 页面加载完成后初始化
        window.addEventListener('DOMContentLoaded', function() {{
            loadPage(1);
            updateButtons();
        }});

        // 加载指定页面
        function loadPage(pageNum) {{
            const pageImage = document.getElementById('pageImage');
            const loading = document.getElementById('loading');

            loading.style.display = 'block';
            pageImage.style.display = 'none';

            const imagePath = `images/page_${{String(pageNum).padStart(3, '0')}}.png`;

            const img = new Image();
            img.onload = function() {{
                pageImage.src = imagePath;
                pageImage.style.display = 'block';
                loading.style.display = 'none';
                applyZoom();
            }};
            img.onerror = function() {{
                loading.innerHTML = '<div>加载失败</div>';
            }};
            img.src = imagePath;

            currentPage = pageNum;
            document.getElementById('pageInput').value = pageNum;
            updateButtons();
        }}

        // 上一页
        function prevPage() {{
            if (currentPage > 1) {{
                loadPage(currentPage - 1);
            }}
        }}

        // 下一页
        function nextPage() {{
            if (currentPage < totalPages) {{
                loadPage(currentPage + 1);
            }}
        }}

        // 跳转到指定页
        function jumpToPage() {{
            const pageInput = document.getElementById('pageInput');
            let pageNum = parseInt(pageInput.value);

            if (pageNum < 1) pageNum = 1;
            if (pageNum > totalPages) pageNum = totalPages;

            loadPage(pageNum);
        }}

        // 更新按钮状态
        function updateButtons() {{
            document.getElementById('prevBtn').disabled = currentPage <= 1;
            document.getElementById('nextBtn').disabled = currentPage >= totalPages;
        }}

        // 放大
        function zoomIn() {{
            zoomLevel = Math.min(zoomLevel + 0.2, 3.0);
            applyZoom();
        }}

        // 缩小
        function zoomOut() {{
            zoomLevel = Math.max(zoomLevel - 0.2, 0.5);
            applyZoom();
        }}

        // 重置缩放
        function resetZoom() {{
            zoomLevel = 1.0;
            applyZoom();
        }}

        // 应用缩放
        function applyZoom() {{
            const pageImage = document.getElementById('pageImage');
            pageImage.style.transform = `scale(${{zoomLevel}})`;
            document.getElementById('zoomLevel').textContent = Math.round(zoomLevel * 100) + '%';
        }}

        // 全屏切换
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}

        // 下载PDF
        function downloadPDF() {{
            const link = document.createElement('a');
            link.href = '../../产业图谱/' + pdfFilename;
            link.download = pdfFilename;
            link.click();
        }}

        // 返回主页
        function goBackHome() {{
            window.location.href = '../../index.html';
        }}

        // 键盘快捷键
        document.addEventListener('keydown', function(e) {{
            switch(e.key) {{
                case 'ArrowLeft':
                    prevPage();
                    break;
                case 'ArrowRight':
                    nextPage();
                    break;
                case 'Escape':
                    if (document.fullscreenElement) {{
                        document.exitFullscreen();
                    }}
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
                case '+':
                case '=':
                    zoomIn();
                    break;
                case '-':
                    zoomOut();
                    break;
                case '0':
                    resetZoom();
                    break;
            }}
        }});
    </script>
</body>
</html>'''

    
    def convert_single_pdf(self, pdf_filename):
        """
        转换单个PDF文件

        Args:
            pdf_filename: PDF文件名
        """
        print(f"\n{'='*60}")
        print(f"开始处理: {pdf_filename}")
        print(f"{'='*60}")

        # 构建路径
        pdf_path = os.path.join(self.pdf_folder, pdf_filename)

        # 检查PDF文件是否存在
        if not os.path.exists(pdf_path):
            print(f"  ❌ 错误: 文件不存在 - {pdf_path}")
            return False

        # 创建输出目录（使用PDF文件名，去掉.pdf扩展名）
        doc_name = os.path.splitext(pdf_filename)[0]
        output_dir = os.path.join(self.output_folder, doc_name)
        os.makedirs(output_dir, exist_ok=True)

        try:
            # 步骤1: 转换PDF为图片
            page_count = self.convert_pdf_to_images(pdf_path, output_dir)

            # 步骤2: 生成HTML页面
            self.generate_html(output_dir, doc_name, page_count, pdf_filename)

            # 步骤3: 保存元数据
            self.save_metadata(output_dir, doc_name, page_count, pdf_filename)

            print(f"\n✅ 成功完成: {pdf_filename}")
            return True

        except Exception as e:
            print(f"\n❌ 转换失败: {pdf_filename}")
            print(f"   错误信息: {str(e)}")
            return False

    def convert_all(self):
        """
        转换所有PDF文件
        """
        print("\n" + "="*60)
        print("PDF转HTML批量转换工具")
        print("="*60)
        print(f"PDF文件夹: {self.pdf_folder}")
        print(f"输出文件夹: {self.output_folder}")
        print(f"图片分辨率: {self.dpi} DPI")
        print("="*60)

        # 创建输出文件夹
        os.makedirs(self.output_folder, exist_ok=True)

        # 获取所有PDF文件
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"\n❌ 在 {self.pdf_folder} 文件夹中没有找到PDF文件")
            return

        print(f"\n找到 {len(pdf_files)} 个PDF文件:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  {i}. {pdf_file}")

        # 转换每个PDF
        success_count = 0
        for pdf_file in pdf_files:
            if self.convert_single_pdf(pdf_file):
                success_count += 1

        # 总结
        print("\n" + "="*60)
        print("转换完成!")
        print(f"成功: {success_count}/{len(pdf_files)}")
        print("="*60)

    def copy_image_to_output(self, source_path, dest_dir):
        """
        复制图片文件到输出目录

        Args:
            source_path: 源图片路径
            dest_dir: 目标目录

        Returns:
            dest_path: 目标文件路径
        """
        import shutil

        # 创建images目录
        images_dir = os.path.join(dest_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 获取文件名
        filename = os.path.basename(source_path)
        dest_path = os.path.join(images_dir, filename)

        # 复制文件
        shutil.copy2(source_path, dest_path)

        return dest_path

    def get_image_html_template(self, title, image_filename, original_image_path):
        """
        获取图片查看器HTML模板

        Args:
            title: 图片标题
            image_filename: 图片文件名
            original_image_path: 原始图片相对路径
        """
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 图片查看器</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
            background: #1a1a1a;
            overflow: hidden;
        }}

        .viewer-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #1a1a1a;
        }}

        /* 顶部工具栏 */
        .toolbar {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            z-index: 100;
        }}

        .toolbar-left {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .toolbar-title {{
            color: #fff;
            font-size: 18px;
            font-weight: 600;
        }}

        .toolbar-right {{
            display: flex;
            gap: 10px;
        }}

        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        /* 主内容区 */
        .content-area {{
            flex: 1;
            display: flex;
            overflow: hidden;
        }}

        /* 图片显示区 */
        .image-display {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: auto;
            padding: 20px;
            position: relative;
        }}

        .image-view {{
            max-width: 100%;
            max-height: 100%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            transition: transform 0.3s;
        }}

        /* 底部控制栏 */
        .controls {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 20px 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
        }}

        .zoom-controls {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .zoom-btn {{
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .zoom-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        .zoom-level {{
            color: #fff;
            font-size: 14px;
            min-width: 60px;
            text-align: center;
        }}

        /* 加载动画 */
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
            font-size: 18px;
        }}

        .spinner {{
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top-color: #4facfe;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .toolbar {{
                padding: 10px 15px;
            }}

            .toolbar-title {{
                font-size: 14px;
            }}

            .btn {{
                padding: 8px 12px;
                font-size: 12px;
            }}

            .controls {{
                padding: 15px;
                flex-wrap: wrap;
            }}
        }}
    </style>
</head>
<body>
    <div class="viewer-container">
        <!-- 顶部工具栏 -->
        <div class="toolbar">
            <div class="toolbar-left">
                <button class="btn btn-primary" onclick="goBackHome()">
                    <span>←</span>
                    <span>返回主页</span>
                </button>
                <div class="toolbar-title">{title}</div>
            </div>
            <div class="toolbar-right">
                <button class="btn btn-secondary" onclick="downloadImage()">
                    <span>📥</span>
                    <span>下载图片</span>
                </button>
                <button class="btn btn-secondary" onclick="toggleFullscreen()">
                    <span>⛶</span>
                    <span>全屏</span>
                </button>
            </div>
        </div>

        <!-- 主内容区 -->
        <div class="content-area">
            <div class="image-display" id="imageDisplay">
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div>加载中...</div>
                </div>
                <img id="imageView" class="image-view" style="display: none;" alt="{title}">
            </div>
        </div>

        <!-- 底部控制栏 -->
        <div class="controls">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomOut()">−</button>
                <div class="zoom-level" id="zoomLevel">100%</div>
                <button class="zoom-btn" onclick="zoomIn()">+</button>
                <button class="zoom-btn" onclick="resetZoom()" title="适应屏幕">⊡</button>
            </div>
        </div>
    </div>

    <script>
        // 全局变量
        let zoomLevel = 1.0;
        const imageFilename = "{image_filename}";
        const originalImagePath = "{original_image_path}";

        // 页面加载完成后初始化
        window.addEventListener('DOMContentLoaded', function() {{
            loadImage();
        }});

        // 加载图片
        function loadImage() {{
            const imageView = document.getElementById('imageView');
            const loading = document.getElementById('loading');

            loading.style.display = 'block';
            imageView.style.display = 'none';

            const imagePath = `images/${{imageFilename}}`;

            const img = new Image();
            img.onload = function() {{
                imageView.src = imagePath;
                imageView.style.display = 'block';
                loading.style.display = 'none';
                applyZoom();
            }};
            img.onerror = function() {{
                loading.innerHTML = '<div>加载失败</div>';
            }};
            img.src = imagePath;
        }}

        // 放大
        function zoomIn() {{
            zoomLevel = Math.min(zoomLevel + 0.2, 3.0);
            applyZoom();
        }}

        // 缩小
        function zoomOut() {{
            zoomLevel = Math.max(zoomLevel - 0.2, 0.5);
            applyZoom();
        }}

        // 重置缩放
        function resetZoom() {{
            zoomLevel = 1.0;
            applyZoom();
        }}

        // 应用缩放
        function applyZoom() {{
            const imageView = document.getElementById('imageView');
            imageView.style.transform = `scale(${{zoomLevel}})`;
            document.getElementById('zoomLevel').textContent = Math.round(zoomLevel * 100) + '%';
        }}

        // 全屏切换
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}

        // 下载图片
        function downloadImage() {{
            const link = document.createElement('a');
            link.href = originalImagePath;
            link.download = imageFilename;
            link.click();
        }}

        // 返回主页
        function goBackHome() {{
            window.location.href = '../../index.html';
        }}

        // 键盘快捷键
        document.addEventListener('keydown', function(e) {{
            switch(e.key) {{
                case 'Escape':
                    if (document.fullscreenElement) {{
                        document.exitFullscreen();
                    }}
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
                case '+':
                case '=':
                    zoomIn();
                    break;
                case '-':
                    zoomOut();
                    break;
                case '0':
                    resetZoom();
                    break;
            }}
        }});
    </script>
</body>
</html>'''

    def convert_single_image(self, image_filename):
        """
        转换单个图片文件为HTML

        Args:
            image_filename: 图片文件名

        Returns:
            bool: 转换是否成功
        """
        print(f"\n{'='*60}")
        print(f"开始处理图片: {image_filename}")
        print(f"{'='*60}")

        # 构建路径
        image_path = os.path.join(self.image_folder, image_filename)

        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            print(f"  ❌ 错误: 文件不存在 - {image_path}")
            return False

        # 创建输出目录（使用图片文件名，去掉扩展名）
        image_name = os.path.splitext(image_filename)[0]
        output_dir = os.path.join(self.image_output_folder, image_name)
        os.makedirs(output_dir, exist_ok=True)

        try:
            # 步骤1: 复制图片到输出目录
            print(f"  正在复制图片...")
            self.copy_image_to_output(image_path, output_dir)
            print(f"  ✅ 图片已复制")

            # 步骤2: 生成HTML页面
            print(f"  正在生成HTML页面...")
            original_image_path = f"../../{self.image_folder}/{image_filename}"
            html_content = self.get_image_html_template(image_name, image_filename, original_image_path)

            html_path = os.path.join(output_dir, "index.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"  ✅ HTML页面已生成: {html_path}")

            # 步骤3: 保存元数据
            print(f"  正在保存元数据...")
            metadata = {
                "title": image_name,
                "type": "image",
                "image_filename": image_filename,
                "format": os.path.splitext(image_filename)[1]
            }

            metadata_path = os.path.join(output_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"  ✅ 元数据已保存")

            print(f"\n✅ 成功完成: {image_filename}")
            return True

        except Exception as e:
            print(f"\n❌ 转换失败: {image_filename}")
            print(f"   错误信息: {str(e)}")
            return False

    def convert_all_images(self):
        """
        转换所有图片文件为HTML
        """
        print("\n" + "="*60)
        print("图片转HTML批量转换工具")
        print("="*60)
        print(f"图片文件夹: {self.image_folder}")
        print(f"输出文件夹: {self.image_output_folder}")
        print("="*60)

        # 检查图片文件夹是否存在
        if not os.path.exists(self.image_folder):
            print(f"\n❌ 图片文件夹不存在: {self.image_folder}")
            return

        # 创建输出文件夹
        os.makedirs(self.image_output_folder, exist_ok=True)

        # 获取所有图片文件
        all_files = os.listdir(self.image_folder)
        image_files = [f for f in all_files
                      if os.path.isfile(os.path.join(self.image_folder, f))
                      and os.path.splitext(f)[1].lower() in self.supported_image_formats]

        if not image_files:
            print(f"\n❌ 在 {self.image_folder} 文件夹中没有找到支持的图片文件")
            print(f"   支持的格式: {', '.join(self.supported_image_formats)}")
            return

        print(f"\n找到 {len(image_files)} 个图片文件:")
        for i, image_file in enumerate(image_files, 1):
            print(f"  {i}. {image_file}")

        # 转换每个图片
        success_count = 0
        for image_file in image_files:
            if self.convert_single_image(image_file):
                success_count += 1

        # 总结
        print("\n" + "="*60)
        print("图片转换完成!")
        print(f"成功: {success_count}/{len(image_files)}")
        print("="*60)


def main():
    """主函数"""
    # 创建转换器实例
    converter = PDFToHTMLConverter(
        pdf_folder="产业图谱",
        output_folder="产业图谱_html",
        dpi=200,
        image_folder="基础知识",
        image_output_folder="基础知识_html"
    )

    # 执行PDF批量转换
    print("\n" + "🔄 开始PDF转换...")
    converter.convert_all()

    # 执行图片批量转换
    print("\n" + "🔄 开始图片转换...")
    converter.convert_all_images()

    # 总结
    print("\n" + "="*60)
    print("✅ 所有转换任务完成！")
    print("="*60)


if __name__ == "__main__":
    main()

