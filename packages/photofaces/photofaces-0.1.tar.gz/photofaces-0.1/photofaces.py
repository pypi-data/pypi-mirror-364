import cv2
from setuptools import setup, find_packages
photo = None
setup(
    name='photofaces',
    version='0.1',
    packages=find_packages(),
    author='MAKSqqqq',
    author_email='cymakswwww@gmail.com',
    description='photofaces',
)
# Путь к изображению
image_path = photo

# Загружаем изображение
image = cv2.imread(image_path)

if image is None:
    print("Не удалось загрузить изображение. Проверьте путь.")
    exit()

# Загружаем предобученный каскадный классификатор для лиц
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Обнаружение лиц
faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)

if len(faces) == 0:
    print("Лица не найдены.")
else:
    for i, (x, y, w, h) in enumerate(faces):
        # Вырезаем лицо
        face_img = image[y:y+h, x:x+w]
        # Сохраняем лицо
        filename = photo
        cv2.imwrite(filename, face_img)
        print(f'Лицо сохранено как {filename}')


cv2.waitKey(0)
cv2.destroyAllWindows()