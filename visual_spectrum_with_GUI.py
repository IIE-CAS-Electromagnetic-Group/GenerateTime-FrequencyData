'''一个小工具，拖动csv进去直接生成瀑布图'''
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from visual_spectrum_single_file import plot_trace_heatmap


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.running = False
        self.progress = None

    def create_widgets(self):
        # 文件选择和显示区域
        self.file_label = tk.Label(self, text=".csv文件路径:")
        self.file_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.file_path = tk.Entry(self, width=80)
        self.file_path.grid(row=0, column=1, padx=10, pady=5)

        # 启用拖放功能
        self.file_path.drop_target_register(DND_FILES)
        self.file_path.dnd_bind('<<Drop>>', self.drop_file)

        self.select_button = tk.Button(self, text="选择文件", command=self.select_file)
        self.select_button.grid(row=0, column=2, padx=10, pady=5)

        # 运行按钮
        self.run_button = tk.Button(self, text="运行", command=self.run_trace)
        self.run_button.grid(row=1, column=0, columnspan=3, pady=10)

        # 状态标签
        self.status = tk.Label(self, text="就绪(可直接将文件拖动到框里)")
        self.status.grid(row=2, column=0, columnspan=3, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, file_path)

    def drop_file(self, event):
        file_path = event.data
        # 处理可能的多文件情况（只取第一个文件）
        if "\n" in file_path:
            file_path = file_path.split("\n")[0]
        # 删除可能的引号
        file_path = file_path.strip('"')

        self.file_path.delete(0, tk.END)
        self.file_path.insert(0, file_path)
        # 自动运行
        self.run_trace()

    def show_progress(self):
        if self.progress:
            self.progress.pack_forget()

        self.progress = tk.Frame(self, height=15, bg="green")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="we", padx=10, pady=5)
        self.update()

        for i in range(50):
            if not self.running:
                break
            self.progress.config(width=80 + i * 2)
            self.update()
            import time
            time.sleep(0.05)

        self.progress.destroy()
        self.progress = None

    def run_trace(self):
        if self.running:
            return

        file_path = self.file_path.get().strip()

        if not file_path:
            messagebox.showwarning("警告", "请先选择或拖入CSV文件")
            return

        if not os.path.isfile(file_path):
            messagebox.showwarning("警告", "无效的文件路径")
            return

        self.running = True
        self.status.config(text="正在运行...")
        self.run_button.config(state=tk.DISABLED)

        self.thread = threading.Thread(target=self.run_trace_in_thread, args=(file_path,))
        self.thread.start()

    def run_trace_in_thread(self, file_path):
        try:
            self.show_progress()
            plot_trace_heatmap(file_path)
            self.master.after(0, self.update_ui_after_run, "成功")
        except Exception as e:
            self.master.after(0, self.show_error, str(e))
        finally:
            self.running = False

    def update_ui_after_run(self, result):
        self.status.config(text=f"{result}")
        self.run_button.config(state=tk.NORMAL)

    def show_error(self, error_message):
        messagebox.showerror("错误", error_message)
        self.status.config(text="就绪")
        self.run_button.config(state=tk.NORMAL)


def main():
    root = TkinterDnD.Tk()  # 使用 TkinterDnD 的 Tk 类
    root.title("时频瀑布图绘制")
    root.geometry("800x150")

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()