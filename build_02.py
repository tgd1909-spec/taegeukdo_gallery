import os
import json
import re

# 01번 전시관과 100% 완벽하게 분리된 도서관 전용 폴더 및 파일 설정
INPUT_DIR = "_archive_docs"
OUTPUT_FILE = "02_data.json"

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Frontmatter(--- 사이의 메타데이터)와 본문(Body) 분리
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        return None

    fm_text, body_text = frontmatter_match.groups()
    
    # 도인 및 도우(道友)님들의 사료 본문 내용 저장
    data = {"body": body_text.strip()}
    
    # 일반 텍스트 정보(제목, 날짜, 분류 등) 추출
    for line in fm_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line and not line.startswith('-'):
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            if key != "images":
                data[key] = val

    # 여러 장의 스캔본 이미지 목록(배열) 깔끔하게 파싱
    images = []
    in_images_section = False
    for line in fm_text.split('\n'):
        if line.strip().startswith('images:'):
            in_images_section = True
            continue
        if in_images_section:
            if line.strip().startswith('-'):
                img_path = re.sub(r'^-\s*(image:\s*)?', '', line.strip()).strip().strip('"\'')
                if img_path:
                    images.append(img_path)
            elif ':' in line and not line.strip().startswith('-'):
                in_images_section = False
                
    data["images"] = images
    
    # 첨부된 PDF가 없을 경우 빈 문자열로 처리하여 에러 방지
    if "pdf_file" not in data or data["pdf_file"] == "null":
        data["pdf_file"] = ""

    return data

def build_json():
    # _archive_docs 폴더가 없으면 자동으로 생성
    if not os.path.exists(INPUT_DIR):
        print(f"[알림] '{INPUT_DIR}' 폴더가 없어 새로 생성합니다.")
        os.makedirs(INPUT_DIR, exist_ok=True)

    archive_list = []
    
    # 폴더 내의 모든 마크다운 문서 읽어오기
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(INPUT_DIR, filename)
            doc_data = parse_markdown(file_path)
            if doc_data:
                doc_data["_filename"] = filename
                archive_list.append(doc_data)

    # 최신 자료가 웹사이트 상단에 먼저 나오도록 정렬 (내림차순)
    archive_list.sort(key=lambda x: x.get("_filename", ""), reverse=True)
    
    for item in archive_list:
        item.pop("_filename", None)

    # 최종 결과물 02_data.json 파일로 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(archive_list, f, ensure_ascii=False, indent=2)
    
    print(f"[완료] 총 {len(archive_list)}개의 자료가 '{OUTPUT_FILE}'(으)로 성공적으로 변환되었습니다!")

if __name__ == "__main__":
    build_json()
