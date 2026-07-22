import os
from PIL import Image, ImageOps, ImageEnhance  # ★ 투명도 조절을 위해 ImageEnhance 추가

UPLOAD_DIR = 'images/uploads'
WATERMARK_PATH = 'watermark.png'
# ★ 추가됨: 로봇이 이미 처리한 사진의 이름을 기록해 둘 장부 파일
LOG_FILE = 'images/uploads/watermark_log.txt' 

if not os.path.exists(WATERMARK_PATH):
    print("워터마크 파일이 없습니다. 경로를 확인해주세요.")
    exit()

watermark = Image.open(WATERMARK_PATH).convert("RGBA")

# 1. 기존에 워터마크를 찍어둔 사진 목록(장부)을 읽어옵니다.
processed_files = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        processed_files = set(f.read().splitlines())

for filename in os.listdir(UPLOAD_DIR):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        
        # 2. 장부에 이미 이름이 있다면 이 사진은 건너뜁니다! (이중 마크 방지)
        if filename in processed_files:
            continue
            
        img_path = os.path.join(UPLOAD_DIR, filename)
        
        try:
            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGBA")
            
            # --- [워터마크 로직 변경 부분 시작] ---
            # 워터마크 크기를 원본 사진 가로 넓이의 40%로 큼직하게 설정
            wm_width = int(img.width * 0.4)
            wm_ratio = wm_width / float(watermark.width)
            wm_height = int(float(watermark.height) * float(wm_ratio))
            wm_resized = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
            
            # 투명도(Opacity) 15% 적용 (0.15 숫자를 조절하여 진하기 변경 가능)
            alpha = wm_resized.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(0.15)
            wm_resized.putalpha(alpha)
            
            # 사진 정중앙에 배치하기 위한 좌표 계산
            position = ((img.width - wm_width) // 2, (img.height - wm_height) // 2)
            # --- [워터마크 로직 변경 부분 끝] ---
            
            transparent = Image.new('RGBA', img.size, (0,0,0,0))
            transparent.paste(img, (0,0))
            transparent.paste(wm_resized, position, mask=wm_resized)
            
            final_img = transparent.convert("RGB")
            final_img.save(img_path, quality=95)
            print(f"{filename} - 자동 회전 및 중앙 반투명 워터마크 적용 완료")
            
            # 3. 방금 워터마크를 찍은 새 사진의 이름을 장부에 추가합니다.
            processed_files.add(filename)
            
        except Exception as e:
            print(f"이미지 처리 중 오류 발생 ({filename}): {e}")

# 4. 새롭게 추가된 이름들을 포함하여 장부를 갱신하여 저장합니다.
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    for pf in processed_files:
        f.write(pf + '\n')
