import os
import zipfile
import datetime
import shutil

def delete_old_archives():
    """删除当前目录下所有旧的打包文件"""
    current_dir = os.getcwd()
    deleted_count = 0
    
    # 遍历当前目录下的所有文件
    for file in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file)
        # 检查是否是打包文件（以"元素周期表系统开发资料_"开头且以".zip"结尾）
        if os.path.isfile(file_path) and file.startswith("元素周期表系统开发资料_") and file.endswith(".zip"):
            try:
                os.remove(file_path)
                print(f"已删除旧打包文件: {file}")
                deleted_count += 1
            except Exception as e:
                print(f"删除文件 {file} 时出错: {e}")
    
    if deleted_count > 0:
        print(f"共删除了 {deleted_count} 个旧打包文件")
    else:
        print("没有找到旧的打包文件")
    
    return deleted_count

def create_archive():
    # 获取当前目录路径
    current_dir = os.getcwd()
    
    # 创建压缩包名称（包含当前日期时间）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"元素周期表系统开发资料_{timestamp}.zip"
    archive_path = os.path.join(current_dir, archive_name)
    
    # 创建ZIP文件
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历当前目录下的所有文件和子目录
        for root, dirs, files in os.walk(current_dir):
            # 跳过脚本自身和已创建的压缩包
            for file in files:
                file_path = os.path.join(root, file)
                # 跳过脚本自身和已创建的压缩包
                if file == os.path.basename(__file__) or file.endswith('.zip'):
                    continue
                
                # 计算相对路径，保持目录结构
                arcname = os.path.relpath(file_path, current_dir)
                
                # 添加文件到压缩包
                zipf.write(file_path, arcname)
                print(f"已添加: {arcname}")
    
    print(f"\n打包完成！压缩包已保存至: {archive_path}")
    print(f"压缩包大小: {os.path.getsize(archive_path) / 1024 / 1024:.2f} MB")
    
    return archive_path

if __name__ == "__main__":
    print("开始打包当前文件夹下的所有资料...")
    
    # 先删除旧的打包文件
    print("\n正在检查并删除旧的打包文件...")
    delete_old_archives()
    
    # 创建新的打包文件
    print("\n开始创建新的打包文件...")
    archive_path = create_archive()
    print("\n打包任务完成！")