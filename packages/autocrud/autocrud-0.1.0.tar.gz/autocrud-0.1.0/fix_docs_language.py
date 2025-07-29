#!/usr/bin/env python3
"""
修正文檔中的語言用詞，從簡體中文轉為繁體中文，並調整台灣慣用詞彙
"""

import os
import re
from pathlib import Path

# 簡體轉繁體對照表
SIMPLIFIED_TO_TRADITIONAL = {
    # 基本字詞轉換
    '用户': '使用者',
    '用戶': '使用者', 
    '創建': '建立',
    '创建': '建立',
    '獲取': '取得',
    '获取': '取得',
    '示例': '範例',
    '筆記本電腦': '筆記型電腦',
    '筆記本电脑': '筆記型電腦',
    '設置': '設定',
    '设置': '設定',
    '配置': '設定',
    '文檔': '文件',
    '文档': '文件',
    '項目': '專案',
    '项目': '專案',
    '數據': '資料',
    '数据': '資料',
    '存儲': '儲存',
    '存储': '儲存',
    '生成': '產生',
    '运行': '執行',
    '運行': '執行',
    '支持': '支援',
    '支援': '支援',
    '默認': '預設',
    '默认': '預設',
    '自定義': '自訂',
    '自定义': '自訂',
    '添加': '新增',
    '批量': '批次',
    '集成': '整合',
    '兼容': '相容',
    '兼容性': '相容性',
    '高級': '進階',
    '高级': '進階',
    '路由': 'routing',
    '中間件': 'middleware',
    '令牌': 'token',
    '依賴': 'dependency',
    '依赖': 'dependency',
    '代碼': '程式碼',
    '代码': '程式碼',
    '推送': 'push',
    '提交': 'commit',
    '克隆': 'clone',
    '倉庫': 'repository',
    '仓库': 'repository',
    '消息': 'message',
    '建置': 'build',
    '質量': '品質',
    '质量': '品質',
    '審查': 'review',
    '庫': '函式庫',
    '库': '函式庫',
    '程序': '程式',
    '程式結束': '程式結束',
    '文件': '檔案',  # 當指檔案時
    '構建': '建置',
    '构建': '建置',
    '實例': '實例',
    '实例': '實例',
    '實現': '實作',
    '实现': '實作',
    '開發': '開發',
    '开发': '開發',
}

def fix_content(content: str) -> str:
    """修正內容中的語言用詞"""
    result = content
    
    # 應用簡繁轉換
    for simplified, traditional in SIMPLIFIED_TO_TRADITIONAL.items():
        result = result.replace(simplified, traditional)
    
    # 特殊處理一些詞組
    result = re.sub(r'創建(\w+)', r'建立\1', result)
    result = re.sub(r'獲取(\w+)', r'取得\1', result)
    result = re.sub(r'用戶(\w+)', r'使用者\1', result)
    result = re.sub(r'數據(\w+)', r'資料\1', result)
    result = re.sub(r'存儲(\w+)', r'儲存\1', result)
    
    return result

def process_markdown_file(file_path: Path):
    """處理單個 Markdown 文件"""
    print(f"處理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixed_content = fix_content(content)
    
    if fixed_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✓ 已更新")
    else:
        print(f"  - 無需更新")

def main():
    """主函數"""
    docs_dir = Path("docs/source")
    
    if not docs_dir.exists():
        print("錯誤: docs/source 目錄不存在")
        return
    
    # 處理所有 Markdown 文件
    markdown_files = list(docs_dir.glob("*.md"))
    
    print(f"找到 {len(markdown_files)} 個 Markdown 文件")
    print("-" * 50)
    
    for md_file in markdown_files:
        process_markdown_file(md_file)
    
    print("-" * 50)
    print("處理完成！")

if __name__ == "__main__":
    main()
