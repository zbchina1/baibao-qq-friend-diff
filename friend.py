import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLD_FILE = os.path.join(BASE_DIR, "好友1.txt")
NEW_FILE = os.path.join(BASE_DIR, "好友2.txt")
TUTORIAL_FILE = os.path.join(BASE_DIR, "介绍与教程.txt")

# ======== 核心修改：严格匹配带有【【【QQ号：的数字 ========
QQ_RE = re.compile(r"【【【QQ号：([1-9]\d{4,11})")

IGNORE_KEYWORDS = ["跳到内容区", "生日祝福", "官方Qzone"]

def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def clean_name(s):
    s = s.strip()
    s = s.strip('"\'')
    s = re.sub(r"^[,，\t;；| ]+|[,，\t;；| ]+$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def parse_friends(text):
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        if any(kw in line for kw in IGNORE_KEYWORDS):
            continue

        m = QQ_RE.search(line)
        if not m:
            continue

        qq = m.group(1)
        before = line[:m.start()]
        after = line[m.end():]

        name = clean_name(before)
        if not name:
            name = clean_name(after)
        if not name:
            name = "（未知昵称）"

        if qq not in result:
            result[qq] = name

    return result

class FriendCompareApp:
    def __init__(self, root):
        self.root = root
        root.title("白宝的QQ好友名单增减对比器")
        root.geometry("560x460")
        root.minsize(460, 340)

        top_bar = tk.Frame(root)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 0))

        tutorial_btn = tk.Button(top_bar, text="介绍和教程", command=self.open_tutorial)
        tutorial_btn.pack(side=tk.LEFT)

        tk.Label(
            root,
            text="请把两次导出的联系人分别保存为：\n好友1.txt（旧）    好友2.txt（新）",
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, padx=12, pady=(8, 4))

        btn = tk.Button(
            root,
            text="开始比对",
            height=2,
            command=self.compare,
            font=("Microsoft YaHei", 11, "bold"),
        )
        btn.pack(fill=tk.X, padx=12, pady=6)

        self.result_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Microsoft YaHei", 10), state=tk.DISABLED)
        self.result_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))

        self.set_result("准备就绪。\n请确认 好友1.txt 和 好友2.txt 与程序在同一文件夹。")

    def set_result(self, text):
        self.result_box.config(state=tk.NORMAL)
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)
        self.result_box.config(state=tk.DISABLED)

    def open_tutorial(self):
        if not os.path.exists(TUTORIAL_FILE):
            messagebox.showwarning("找不到文件", f"找不到介绍与教程文件：\n{TUTORIAL_FILE}")
            return
        try:
            os.startfile(TUTORIAL_FILE)
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def show_list_window(self, title, qq_list, friend_dict):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("340x420")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        lines = [f"{friend_dict[qq]}（{qq}）" for qq in qq_list]
        text.insert(tk.END, "\n".join(lines))
        text.config(state=tk.DISABLED)

    def compare(self):
        if not os.path.exists(OLD_FILE):
            messagebox.showerror("缺少文件", f"找不到：\n{OLD_FILE}")
            return
        if not os.path.exists(NEW_FILE):
            messagebox.showerror("缺少文件", f"找不到：\n{NEW_FILE}")
            return

        try:
            old_text = read_text(OLD_FILE)
            new_text = read_text(NEW_FILE)
        except Exception as e:
            messagebox.showerror("读取失败", str(e))
            return

        old_friends = parse_friends(old_text)
        new_friends = parse_friends(new_text)

        old_keys = set(old_friends.keys())
        new_keys = set(new_friends.keys())

        added = sorted(new_keys - old_keys, key=lambda x: int(x))
        removed = sorted(old_keys - new_keys, key=lambda x: int(x))

        if not added and not removed:
            self.set_result("嗯...没有变化呢，一切正常")
            return

        if added and removed:
            self.set_result("啊！你的好友同时有增加和减少，我们来看看吧\n\n已打开两个窗口分别显示。")
            self.show_list_window("新增好友名单", added, new_friends)
            self.show_list_window("减少好友名单", removed, old_friends)
            return

        if added:
            lines = ["你好像有了新朋友："]
            for qq in added: lines.append(f"{new_friends[qq]}（{qq}）")
            lines.append(f"\n统计：新增 {len(added)} 人。")
            self.set_result("\n".join(lines))
            return

        if removed:
            lines = ["啊哦！好像有朋友和你的好友关系取消了："]
            for qq in removed: lines.append(f"{old_friends[qq]}（{qq}）")
            lines.append(f"\n统计：减少 {len(removed)} 人。")
            self.set_result("\n".join(lines))
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = FriendCompareApp(root)
    root.mainloop()