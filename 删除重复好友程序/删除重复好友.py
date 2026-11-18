import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

# 严格匹配带有前缀的 QQ 号
QQ_RE = re.compile(r'【【【QQ号：([1-9]\d{4,11})')

def parse_friends_line(line):
    matches = list(QQ_RE.finditer(line))
    if not matches:
        return []
    
    results = []
    last_end = 0
    for idx, match in enumerate(matches):
        qq = match.group(1)
        # 名字取前缀前面的内容
        before = line[last_end:match.start()].strip()
        # 如果前缀后面还有内容（一般没有，防万一）
        after = line[match.end(): (matches[idx+1].start() if idx+1 < len(matches) else len(line))].strip()
        
        name = before if before else after
        if not name:
            name = "（未知昵称）"
            
        results.append((qq, name))
        last_end = match.end()
        
    return results

class CleanApp:
    def __init__(self, root):
        self.root = root
        root.title("清理重复好友与整理格式")
        root.geometry("500x400")
        
        tk.Label(root, text="请选择要清理的好友 txt 文件（例如 好友1.txt）", font=("Microsoft YaHei", 10)).pack(pady=10)
        
        tk.Button(root, text="选择文件并清理", command=self.clean_file, font=("Microsoft YaHei", 10, "bold"), bg="#f0f0f0").pack(pady=5)
        
        self.result_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def clean_file(self):
        filepath = filedialog.askopenfilename(
            title="选择好友名单文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not filepath:
            return
            
        lines = []
        for enc in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
            try:
                with open(filepath, "r", encoding=enc) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
        seen_qqs = set()
        output_lines = []
        original_count = 0
        duplicate_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            friends = parse_friends_line(line)
            for qq, name in friends:
                original_count += 1
                if qq in seen_qqs:
                    duplicate_count += 1
                    continue
                seen_qqs.add(qq)
                # 统一输出为：名字 【【【QQ号：号码
                output_lines.append(f"{name} 【【【QQ号：{qq}")
                
        dir_name = os.path.dirname(filepath)
        base_name = os.path.basename(filepath)
        name, ext = os.path.splitext(base_name)
        out_file = os.path.join(dir_name, f"{name}_去重整理后{ext}")
        
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines))
            
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, f"✅ 清理完成！\n\n")
            self.result_box.insert(tk.END, f"原始数据解析出 {original_count} 个 QQ 号。\n")
            self.result_box.insert(tk.END, f"发现并删除了 {duplicate_count} 个重复的 QQ 号。\n")
            self.result_box.insert(tk.END, f"最终保留了 {len(output_lines)} 位好友。\n\n")
            self.result_box.insert(tk.END, f"保存位置：\n{out_file}")
            
            messagebox.showinfo("成功", f"清理成功！\n生成文件：{name}_去重整理后{ext}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = CleanApp(root)
    root.mainloop()