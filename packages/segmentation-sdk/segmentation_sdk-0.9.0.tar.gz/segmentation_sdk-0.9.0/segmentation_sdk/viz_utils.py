import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
 
# Optional import for jcv2 (only if in GUI-supported environment)
try:
    import opencv_jupyter_ui as jcv2
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
 
def get_class_colors(n):
    if n > 21:
        raise Exception('Exceeded maximum number of classes.')
    COLORS = [(0, 0, 0)] + list(sns.color_palette('tab20'))
    COLORS = (np.array(COLORS) * 255.0).astype(np.uint8)
    COLORS = np.flip(COLORS, axis=1)
    return COLORS[:n]
 
def pad_with_text(x, text):
    x = cv2.resize(x, None, fx=2.0, fy=2.0)
    x = np.pad(x, ((100, 0), (0, 0), (0, 0)), 'constant', constant_values=0)
    x = cv2.putText(x, text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    2.0, (255, 255, 255), 4, cv2.LINE_AA)
    return cv2.resize(x, None, fx=0.5, fy=0.5)
 
def get_plt_canvas(fig):
    fig.canvas.draw()
    image_flat = np.frombuffer(fig.canvas.tostring_argb(), dtype='uint8')
    image = image_flat.reshape(*reversed(fig.canvas.get_width_height()), 4)
    return image
 
def get_class_names_img(class_names, colors):
    class_names_img = np.full((len(class_names)*50 + 20, 650, 3), 50).astype(np.uint8)
 
    for idx, category in enumerate(class_names):
        color = tuple(int(x) for x in colors[category['id']])
        start_point = (10, 10 + idx * 50)
        end_point = (250, 10 + (idx + 1) * 50)
        text_point = (260, 45 + idx * 50)
 
        class_names_img = cv2.rectangle(class_names_img, start_point, end_point, color, -1)
        class_names_img = cv2.putText(class_names_img, category['name'], text_point,
                                      cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    return class_names_img
 
def viz_img(img, name, text=None, save_path=None):
    img = img.astype(np.uint8)
    if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if text:
        cv2.putText(img, text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2, cv2.LINE_AA)
 
    if save_path:
        cv2.imwrite(save_path, img)
    elif GUI_AVAILABLE:
        try:
            jcv2.imshow(name, img)
        except Exception as e:
            print(f"GUI display failed: {e}")
    else:
        print(f"Display not supported in this environment. Set `save_path` to save the image instead.")
 
def plot_images(images: list, cmaps: list = None, size_inches=(20, 20)) -> None:
    fig, axes = plt.subplots(1, len(images))
    fig.set_size_inches(size_inches)
    for i, (axis, img) in enumerate(zip(axes, images)):
        cmap = cmaps[i] if cmaps else "viridis"
        axis.axis("off")
        axis.imshow(img, cmap=cmap)
    plt.show()