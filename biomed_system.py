import sqlite3
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


# 1. طبقة إدارة قاعدة البيانات (DATABASE MANAGEMENT - SQLITE3)
# الهدف: تخزين معلومات الأجهزة وسجلات القياسات الحية لتكون مرجعاً تاريخياً للمستشفى.
class MedicalDB:
    def __init__(self, db_name="clinical_fleet.db"):
        # إنشاء اتصال بقاعدة البيانات المحلية (SQLite) وتوليد الملف إذا لم يكن موجوداً
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()  # المؤشر المسؤول عن تنفيذ أوامر SQL داخل قاعدة البيانات
        self.create_tables()  # استدعاء دالة بناء الجداول فور بدء التشغيل

    def create_tables(self):
        # 1. جدول الأجهزة الطبية (Equipment): يحفظ معلومات الأجهزة وأماكنها وتواريخ تركيبها
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL,
                install_date TEXT NOT NULL
            )
        ''')
       
        # 2. جدول سجلات التيليمتري (Telemetry Logs): يسجل القراءات الحية المتدفقة لكل جهاز
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                timestamp TEXT,
                temperature REAL,
                current_draw REAL,
                vibration REAL,
                wear_index REAL,
                alert_status TEXT,
                FOREIGN KEY(device_id) REFERENCES equipment(id)
            )
        ''')
       
        # حقن بيانات أولية (Seeding) في حال كان الجدول فارغاً لتوفير أجهزة جاهزة للمراقبة فوراً
        self.cursor.execute("SELECT COUNT(*) FROM equipment")
        if self.cursor.fetchone()[0] == 0:
            default_devices = [
                ("Ventilator-X900", "ICU-A", "Active", "2024-01-15"),
                ("InfusionPump-P200", "ICU-B", "Active", "2024-03-10"),
                ("Incubator-N30", "NICU", "Active", "2023-11-20"),
                ("DialysisMachine-D50", "Nephrology", "Active", "2024-05-05")
            ]
            self.cursor.executemany("INSERT INTO equipment (device_name, department, status, install_date) VALUES (?, ?, ?, ?)", default_devices)
            self.conn.commit()  # حفظ التغييرات واعتمادها في ملف القاعدة

    def log_telemetry(self, device_id, temp, current, vib, wear, status):
        # دالة لإدخال سجل قياس جديد في قاعدة البيانات لكل دورة محاكاة زمنية
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO telemetry_logs (device_id, timestamp, temperature, current_draw, vibration, wear_index, alert_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (device_id, timestamp, temp, current, vib, wear, status))
        self.conn.commit()

    def get_all_equipment(self):
        # جلب كافة الأجهزة المسجلة لعرضها في الجداول والقوائم المنسدلة
        self.cursor.execute("SELECT * FROM equipment")
        return self.cursor.fetchall()

    def close(self):
        # إغلاق الاتصال بقاعدة البيانات عند إنهاء التطبيق
        self.conn.close()

# 2. الواجهة الرسومية ومركز مراقبة التيليمتري (MAIN GUI & TELEMETRY CONTROL CENTER)

class MedicalFleetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Medical Equipment Fleet Telemetry & Predictive Maintenance")
        self.root.geometry("1100x700")
        self.root.configure(bg="#1e1e2f")  # تعيين لون خلفية نافذة البرنامج الرئيسية

        self.db = MedicalDB()  # ربط الواجهة بقاعدة البيانات
        self.selected_device_id = 1  # الجهاز الافتراضي المحدد للمراقبة
        self.running_simulation = True  # متغير للتحكم بتشغيل حلقة المحاكاة الحية

        # تخصيص واجهة المستخدم (Theming with TTK) لتناسب المظهر الداكن (Dark Mode)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#1e1e2f", foreground="#ffffff", fieldbackground="#2d2d44")
        self.style.configure("TNotebook", background="#1e1e2f", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#2d2d44", foreground="#ffffff", padding=[15, 8], font=("Arial", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", "#00adb5")], foreground=[("selected", "#ffffff")])

        # إطار العنوان العلوي للبرنامج
        header_frame = tk.Frame(root, bg="#111118", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
       
        title_label = tk.Label(header_frame, text=" CLINICAL ENGINEERING TELEMETRY & PREDICTIVE TRIAGE CENTER",
                               bg="#111118", fg="#00adb5", font=("Arial", 15, "bold"))
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # إنشاء نظام التبويبات (Notebook) للفصل بين لوحة المراقبة الحية ومخزون الأجهزة
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # التبويب الأول: لوحة المراقبة الحية (Live Telemetry Dashboard)
        self.tab_monitor = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(self.tab_monitor, text="  Live Telemetry Dashboard  ")
        self.setup_monitor_tab()

        # التبويب الثاني: جدول مخزون الأجهزة في المستشفى (Equipment Fleet Inventory)
        self.tab_fleet = tk.Frame(self.notebook, bg="#1e1e2f")
        self.notebook.add(self.tab_fleet, text="  Equipment Fleet Inventory  ")
        self.setup_fleet_tab()

        # بدء حلقة التحديث المستمر للتيليمتري بعد ثانية واحدة من التشغيل
        self.root.after(1000, self.update_telemetry_loop)

    def setup_monitor_tab(self):
        # اللوحة اليسرى: تحتوي على القائمة المنسدلة لاختيار الجهاز وقيم القياسات الحية
        left_panel = tk.Frame(self.tab_monitor, bg="#252538", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(left_panel, text="Select Equipment Fleet Unit:", bg="#252538", fg="#ffffff", font=("Arial", 11, "bold")).pack(anchor="w", padx=15, pady=10)

        # تجهيز قائمة الأجهزة لاختيار الجهاز المراد مراقبته
        self.device_var = tk.StringVar()
        self.devices = self.db.get_all_equipment()
        self.device_names = [f"{d[0]} - {d[1]} ({d[2]})" for d in self.devices]
        self.device_var.set(self.device_names[0])

        self.device_dropdown = ttk.Combobox(left_panel, textvariable=self.device_var, values=self.device_names, state="readonly", width=35)
        self.device_dropdown.pack(padx=15, pady=5)
        self.device_dropdown.bind("<<ComboboxSelected>>", self.on_device_selected)

        # إطار المعايير التشخيصية (Diagnostic Parameters Panel)
        metrics_frame = tk.LabelFrame(left_panel, text=" Real-Time Diagnostic Parameters ", bg="#252538", fg="#00adb5", font=("Arial", 10, "bold"), bd=2, relief="groove")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=20)

        # نصوص عرض القيم الحية (الحرارة، التيار، الاهتزاز، التآكل، وحالة النظام)
        self.lbl_temp = tk.Label(metrics_frame, text="Core Temperature: -- °C", bg="#252538", fg="#ffffff", font=("Arial", 11), anchor="w")
        self.lbl_temp.pack(fill=tk.X, padx=15, pady=12)

        self.lbl_current = tk.Label(metrics_frame, text="Current Draw: -- A", bg="#252538", fg="#ffffff", font=("Arial", 11), anchor="w")
        self.lbl_current.pack(fill=tk.X, padx=15, pady=12)

        self.lbl_vib = tk.Label(metrics_frame, text="Mechanical Vibration: -- mm/s", bg="#252538", fg="#ffffff", font=("Arial", 11), anchor="w")
        self.lbl_vib.pack(fill=tk.X, padx=15, pady=12)

        self.lbl_wear = tk.Label(metrics_frame, text="Wear & Tear Index: -- %", bg="#252538", fg="#eeeeee", font=("Arial", 11, "bold"), anchor="w")
        self.lbl_wear.pack(fill=tk.X, padx=15, pady=12)

        self.lbl_alert_status = tk.Label(metrics_frame, text="SYSTEM STATUS: STABLE", bg="#252538", fg="#2ecc71", font=("Arial", 12, "bold"))
        self.lbl_alert_status.pack(fill=tk.X, padx=15, pady=20)

        # اللوحة اليمنى: شاشة رسم إشارات التيليمتري الحية (Canvas Waveform Screen)
        right_panel = tk.Frame(self.tab_monitor, bg="#111118")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(right_panel, text="LIVE CLINICAL TELEMETRY WAVEFORM SIGNATURE", bg="#111118", fg="#00adb5", font=("Arial", 12, "bold")).pack(pady=15)

        # عنصر الـ Canvas المسؤول عن رسم الموجات التذبذبية ديناميكياً
        self.signal_canvas = tk.Canvas(right_panel, bg="#0b0b10", height=380, highlightthickness=1, highlightbackground="#00adb5")
        self.signal_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.lbl_waveform_note = tk.Label(right_panel, text="Status: Real-time telemetry data streaming active...", bg="#111118", fg="#888888", font=("Arial", 10))
        self.lbl_waveform_note.pack(pady=10)

    def setup_fleet_tab(self):
        # إعداد تبويب جدول مخزون الأجهزة باستخدام Treeview
        table_frame = tk.Frame(self.tab_fleet, bg="#1e1e2f")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        columns = ("ID", "Device Name", "Department", "Status", "Install Date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")
       
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.load_fleet_data()  # تحميل البيانات وسحبها من قاعدة البيانات لعرضها في الجدول

    def load_fleet_data(self):
        # تفريغ الجدول أولاً ثم تعبئته بالبيانات الحالية من قاعدة البيانات
        for row in self.tree.get_children():
            self.tree.delete(row)
        for dev in self.db.get_all_equipment():
            self.tree.insert("", tk.END, values=dev)

    def on_device_selected(self, event):
        # دالة يتم استدعاؤها عند تغيير الجهاز من القائمة المنسدلة لمعرفة أي جهاز يتم مراقبته حالياً
        selected_text = self.device_var.get()
        self.selected_device_id = int(selected_text.split(" - ")[0])

    def update_telemetry_loop(self):
        # حلقة المحاكاة الحية المتجددة (تتنفذ كل ثانيتين لإنشاء بيئة تيليمتري حية)
        if not self.running_simulation:
            return

        # 1. توليد قراءات افتراضية واقعية باستخدام العشوائية المدروسة (Random Simulation)
        temp = round(random.uniform(36.5, 43.5), 2)  # درجة الحرارة الداخلية
        current = round(random.uniform(1.2, 4.8), 2)  # سحب التيار الكهربائي بالآمبير
        vib = round(random.uniform(0.1, 2.5), 2)     # الاهتزاز الميكانيكي
       
        # 2. معادلة التنبؤ بالتآكل (Wear & Teo Index Formula): معادلة هندسية تحسب نسبة الإجهاد
        wear = round((temp - 36) * 12 + (current * 5) + (vib * 10), 1)
        if wear > 100: wear = 100.0  # الحد الأقصى للتآكل هو 100%

        # 3. منطق تقييم الحالة والإنذارات (Threshold Logic) بناءً على القيم الحالية
        status_text = "SYSTEM STATUS: STABLE"
        status_color = "#2ecc71"  # أخضر للحالة المستقرة
        if temp > 41.5 or current > 4.2 or wear > 80:
            status_text = "CRITICAL: PREDICTIVE FAILURE RISK!"
            status_color = "#e74c3c"  # أحمر لخطر الفشل الوشيك
        elif temp > 39.5 or current > 3.5 or wear > 60:
            status_text = "WARNING: HIGH WEAR DETECTED"
            status_color = "#f1c40f"  # أصفر لتحذير التآكل العالي

        # 4. تحديث النصوص الظاهرة على الواجهة الرسومية بالقيم الجديدة
        self.lbl_temp.config(text=f"Core Temperature: {temp} °C")
        self.lbl_current.config(text=f"Current Draw: {current} A")
        self.lbl_vib.config(text=f"Mechanical Vibration: {vib} mm/s")
        self.lbl_wear.config(text=f"Wear & Tear Index: {wear} %")
        self.lbl_alert_status.config(text=status_text, fg=status_color)

        # 5. رسم الموجات الحية المتذبذبة على شاشة الـ Canvas ديناميكياً
        self.signal_canvas.delete("wave")  # مسح الموجة القديمة لمنع التداخل
        width = self.signal_canvas.winfo_width()
        height = self.signal_canvas.winfo_height()
        if width < 100: width = 600
        if height < 100: height = 380

        points = []
        step = width / 30
        for i in range(30):
            x = i * step
            # تحديد محور y بناءً على منتصف الشاشة متأثراً بالحرارة والقيم العشوائية
            y = (height / 2) + ((random.uniform(-1, 1) * 30) + ((temp - 39) * 15))
            points.append((x, y))

        flat_points = [coord for pt in points for coord in pt]
        if len(flat_points) >= 4:
            self.signal_canvas.create_line(flat_points, fill="#00adb5", width=2, smooth=True, tags="wave")

        # 6. حفظ السجل الجديد في قاعدة البيانات (SQLite Telemetry Logging)
        self.db.log_telemetry(self.selected_device_id, temp, current, vib, wear, status_text)
       
        # 7. جدولة تشغيل الدالة مرة أخرى بعد 2000 مللي ثانية (2 ثانية) بشكل مستمر دون تجميد النافذة
        self.root.after(2000, self.update_telemetry_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalFleetApp(root)
    root.mainloop() 