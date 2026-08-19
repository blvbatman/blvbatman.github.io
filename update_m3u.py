import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/vmttv"
TARGET_FILE = "app.m3u"

def fetch_m3u(url):
    req = urllib.request.urlopen(url)
    return req.read().decode('utf-8', errors='ignore').splitlines()

def is_fpt_group(line):
    return "Sự Kiện FPT PLAY" in line

def extract_valid_channels(lines):
    valid_channels = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Tìm thấy dòng bắt đầu của kênh thuộc group FPT Play
        if line.startswith("#EXTINF:") and is_fpt_group(line):
            channel_block = [line]
            i += 1
            # Đọc tiếp các dòng phía dưới cho đến khi gặp dòng bắt đầu bằng #EXTINF mới hoặc hết file
            while i < len(lines) and not lines[i].startswith("#EXTINF:"):
                channel_block.append(lines[i])
                i += 1
            
            # Kiểm tra điều kiện: Block hợp lệ phải có độ dài từ 2 đến 3 dòng 
            # (1 dòng #EXTINF, 1 dòng link stream, hoặc có thêm 1 dòng phụ tùy biến nhưng tối đa không quá 3 dòng trước khi tới #EXTINF tiếp theo)
            if 2 <= len(channel_block) <= 3:
                valid_channels.extend(channel_block)
            # Nếu block nhiều hơn 3 dòng (tức là bị rác hoặc lỗi cấu trúc), nó sẽ tự động bị bỏ qua
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
            # Bỏ qua toàn bộ các dòng thuộc khối kênh đó cho đến khi gặp #EXTINF kế tiếp
            while i < len(lines) and not lines[i].startswith("#EXTINF:"):
                i += 1
            continue
        cleaned.append(line)
        i += 1
    return cleaned

def process_m3u():
    try:
        # 1. Tải và lọc sạch các block kênh từ nguồn mẫu (đã loại bỏ mấy khối > 3 dòng)
        source_lines = fetch_m3u(SOURCE_URL)
        new_fpt_channels = extract_valid_channels(source_lines)

        # 2. Đọc file app.m3u hiện tại
        try:
            with open(TARGET_FILE, "r", encoding="utf-8", errors='ignore') as f:
                target_lines = f.read().splitlines()
        except FileNotFoundError:
            target_lines = ["#EXTM3U"]

        # 3. Xóa nhóm FPT Play cũ trong file của bạn
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
            
        print("Cập nhật và lọc kênh lỗi thành công!")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    process_m3u()
