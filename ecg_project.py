import wfdb
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

print("جاري تحميل إشارة القلب الحقيقية من قاعدة البيانات...")

# 1. تحميل إشارة ECG تجريبية من قاعدة بيانات PhysioNet
record_name = '100'
signals, fields = wfdb.rdsamp(record_name, pn_dir='mitdb', sampto=2000)
ecg_signal = signals[:, 0] # أخذ القناة الأولى للإشارة

# 2. تصميم فلتر رقمي لتنظيف الإشارة (Bandpass Filter)
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

fs = 360  # معدل أخذ العينات
filtered_ecg = bandpass_filter(ecg_signal, 0.5, 50.0, fs)

print("تم المعالجة بنجاح! جاري رسم النتائج...")

# 3. رسم النتيجة ومقارنة الإشارة قبل وبعد التنظيف
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(ecg_signal, color='red')
plt.title('Raw ECG Signal (With Noise) - إشارة القلب الخام')
plt.ylabel('Amplitude')

plt.subplot(2, 1, 2)
plt.plot(filtered_ecg, color='green')
plt.title('Filtered ECG Signal (Cleaned) - إشارة القلب بعد الفلترة والتنظيف')
plt.xlabel('Samples')
plt.ylabel('Amplitude')

plt.tight_layout()
plt.savefig('ecg_result.png') # حفظ الصورة تلقائياً
plt.show()

print("تم حفظ الصورة بنجاح باسم ecg_result.png في مجلد المشروع!")