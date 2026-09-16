import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color, filters, util

print("جاري إنشاء وتحميل عينة صورة طبية تحليلية...")

# 1. إنشاء صورة طبية افتراضية تحاكي مقطع رنين مغناطيسي (MRI Slice) لتجربة الخوارزمية عليها
# (دائرة تمثل الدماغ وبداخلها كتلة تمثل الورم المراد عزله)
mri_image = np.zeros((300, 300), dtype=float)
# إضافة جمجمة أو رأس افتراضي
rr, cc = np.ogrid[:300, :300]
brain_mask = (rr - 150)**2 + (cc - 150)**2 <= 100**2
mri_image[brain_mask] = 0.6

# إضافة "ورم" أو منطقة اهتمام باختلاف شدة الإضاءة داخل الدماغ
tumor_mask = (rr - 130)**2 + (cc - 120)**2 <= 20**2
mri_image[tumor_mask] = 1.0

# إضافة بعض التشويش الطبيعي للصورة (Noise) لتكون واقعية
noisy_mri = util.random_noise(mri_image, mode='gaussian', var=0.01)

# 2. تطبيق خوارزمية التجزئة الطبية (Threshold Segmentation) لعزل الورم والمنطقة المصابة
thresh = filters.threshold_otsu(noisy_mri)
segmentation = noisy_mri > thresh

print("تمت معالجة وتحليل الصورة الطبية بنجاح!")

# 3. رسم ومقارنة النتائج وحفظها
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(noisy_mri, cmap='gray')
plt.title('Original MRI Scan (صورة الرنين الخام)')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(segmentation, cmap='gray')
plt.title('Tumor/Region Segmentation (عزل وتجزئة الورم هندسياً)')
plt.axis('off')

plt.tight_layout()
plt.savefig('mri_result.png')
print("تم حفظ نتيجة المشروع الثاني باسم mri_result.png بنجاح!")
plt.show()