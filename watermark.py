import os
from PIL import Image

# 경로 설정
UPLOAD_DIR = "images/uploads"
WATERMARK_FILE = "watermark.png"

def apply_watermark():
    if not os.path.exists(WATERMARK_FILE):
        print("워터마크 파일이 없습니다.")
        return

    # 투명도를 유지하며 워터마크 이미지 열기
    watermark = Image.open(WATERMARK_FILE).convert("RGBA")
    
    for filename in os.listdir(UPLOAD_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            try:
                base_image = Image.open(filepath).convert("RGBA")
                
                wm_width, wm_height = watermark.size
                base_width, base_height = base_image.size
                
                # 워터마크 크기를 원본 사진 가로 폭의 20% 크기로 자동 조절
                scale = (base_width * 0.2) / wm_width
                new_wm_size = (int(wm_width * scale), int(wm_height * scale))
                resized_wm = watermark.resize(new_wm_size, Image.Resampling.LANCZOS)
                
                # 우측 하단에 배치 (여백 20px)
                position = (base_width - new_wm_size[0] - 20, base_height - new_wm_size[1] - 20)
                
                # 합성 작업
                transparent = Image.new('RGBA', (base_width, base_height), (0,0,0,0))
                transparent.paste(base_image, (0,0))
                transparent.paste(resized_wm, position, mask=resized_wm)
                
                # JPG 포맷으로 덮어쓰기 저장
                final_image = transparent.convert("RGB")
                final_image.save(filepath, "JPEG")
                print(f"{filename}에 워터마크가 적용되었습니다.")
                
            except Exception as e:
                print(f"{filename} 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    if os.path.exists(UPLOAD_DIR):
        apply_watermark()
