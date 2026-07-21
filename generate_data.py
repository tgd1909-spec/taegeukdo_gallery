import os
import json
import yaml

folder_path = '_exhibition'
output_file = 'gallery_data.json'
data_list = []

# _exhibition 폴더의 모든 파일을 확인
if os.path.exists(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # --- 기호를 기준으로 설정값(YAML)과 본문(Body) 분리
            parts = content.split('---')
            if len(parts) >= 3:
                front_matter = parts[1]
                body_text = '---'.join(parts[2:]).strip()
                
                # 데이터를 하나로 병합
                try:
                    item = yaml.safe_load(front_matter)
                    if item:
                        item['body'] = body_text
                        data_list.append(item)
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")

# JSON 파일로 최종 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)
