import os
from PIL import Image, ImageOps

# [설정 부분] 경로와 파일명
UPLOAD_DIR = 'images/uploads'
WATERMARK_PATH = 'watermark.png'

# 워터마크 파일 존재 여부 확인
if not os.path.exists(WATERMARK_PATH):
    print("워터마크 파일이 없습니다. 경로를 확인해주세요.")
    exit()

# 워터마크 이미지 불러오기
watermark = Image.open(WATERMARK_PATH).convert("RGBA")

# 업로드 폴더 내의 모든 이미지 파일 처리
for filename in os.listdir(UPLOAD_DIR):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        img_path = os.path.join(UPLOAD_DIR, filename)
        
        try:
            # 1. 원본 이미지 불러오기
            img = Image.open(img_path)
            
            # ★ 핵심: 스마트폰 방향 정보(EXIF)를 읽어 사진을 올바르게 자동 회전시킵니다.
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGBA")
            
            # 2. 워터마크 크기 조절 (원본 이미지 가로의 15% 비율로 설정)
            wm_width = int(img.width * 0.15)
            wm_ratio = wm_width / float(watermark.width)
            wm_height = int(float(watermark.height) * float(wm_ratio))
            wm_resized = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
            
            # 3. 워터마크 위치 설정 (우측 하단, 여백 20px)
            margin = 20
            position = (img.width - wm_width - margin, img.height - wm_height - margin)
            
            # 4. 워터마크 합성 (투명한 배경에 원본과 워터마크를 겹침)
            transparent = Image.new('RGBA', img.size, (0,0,0,0))
            transparent.paste(img, (0,0))
            transparent.paste(wm_resized, position, mask=wm_resized)
            
            # 5. 최종 이미지 저장 (JPG 등을 위해 RGB 모드로 변환 후 덮어쓰기)
            final_img = transparent.convert("RGB")
            final_img.save(img_path, quality=95)
            print(f"{filename} - 자동 회전 및 워터마크 적용 완료")
            
        except Exception as e:
            print(f"이미지 처리 중 오류 발생 ({filename}): {e}")
