import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/vmttv"
TARGET_FILE = "app.m3u"

def fetch_m3u(url):
    req = urllib.request.urlopen(url)
    return req.read().decode('utf-8', errors='ignore').splitlines()

def is_fpt_group(line):
    # Nhận diện cả "Sự Kiện FPT PLAY" hoặc "Sự Kiện FPT"
    return "Sự Kiện FPT" in line

def extract_valid_channels(lines):
    valid_channels = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:") and is_fpt_group(line):
            channel_block = [line]
            i += 1
            # Đọc tiếp các dòng phía dưới cho đến khi gặp #EXTINF mới hoặc hết file
            while i < len(lines) and not lines[i].startswith("#EXTINF:"):
                channel_block.append(lines[i])
                i += 1
            
            # Kiểm tra độ dài block hợp lệ (từ 2 đến 3 dòng)
            if 2 <= len(channel_block) <= 3:
                # Kiểm tra link stream bên trong block có chứa 'm3u8' không và KHÔNG chứa 'mpd'
                block_str = "\n".join(channel_block)
                has_m3u8 = "m3u8" in block_str.lower()
                has_mpd = "mpd" in block_str.lower()
                
                # Chỉ lấy nếu có m3u8 và không có mpd
                if has_m3u8 and not has_mpd:
                    valid_channels.extend(channel_block)
            continue
        else:
            i += 1
    return valid_channels

def remove_fpt_group(lines):
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:") and is_fpt_group(line):
            i += 1
            # Bỏ qua toàn bộ khối kênh thuộc nhóm FPT cũ trong file của bạn
            while i < len(lines) and not lines[i].startswith("#EXTINF:"):
                i += 1
            continue
        cleaned.append(line)
        i += 1
    return cleaned

def process_m3u():
    try:
        # 1. Tải và lọc các kênh thỏa mãn điều kiện từ nguồn
        source_lines = fetch_m3u(SOURCE_URL)
        new_fpt_channels = extract_valid_channels(source_lines)

        # 2. Đọc file app.m3u hiện tại của bạn
        try:
            with open(TARGET_FILE, "r", encoding="utf-8", errors='ignore') as f:
                target_lines = f.read().splitlines()
        except FileNotFoundError:
            target_lines = ["#EXTM3U"]

        # 3. Xóa nhóm FPT / FPT Play cũ trong file của bạn
        cleaned_target = remove_fpt_group(target_lines)

        # 4. Chèn nhóm kênh mới vào ngay sau dòng #EXTM3U
        final_lines = []
        inserted = False
        for line in cleaned_target:
            final_lines.append(line)
            if line.startswith("#EXTM3U") and not inserted:
                final_lines.extend(new_fpt_channels)
                inserted = True
                
        if not inserted:
            final_lines = new_fpt_channels + cleaned_target

        # 5. Lưu lại file
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines) + "\n")
            
        print("Cập nhật, lọc nhóm FPT và loại bỏ định dạng MPD thành công!")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    process_m3u()
