import pandas as pd
import re

def process_salary(salary_str):
    """
    Hàm này xử lý một chuỗi lương và trả về (min_salary, max_salary, avg_salary) bằng VND.
    """
    if not isinstance(salary_str, str):
        return None, None, None

    original_str = salary_str.strip()
    salary_lower = original_str.lower()
    
    # Các từ khóa cho lương không phải dạng số
    non_numeric_keywords = [
        'you\'ll love it', 'negotiable', 'thỏa thuận', 'thương lượng', 
        'attractive', 'competitive', 'let\'s discuss', 'based on experience',
        'open for your best rate', 'login to view salary', 'negotation',
        'high salary'
    ]
    if any(keyword in salary_lower for keyword in non_numeric_keywords):
        return None, None, None

    min_salary, max_salary = None, None
    usd_to_vnd = 26000

    # Helper nội bộ để chuyển một số + đơn vị sang VND (không áp dụng cho khoảng, chỉ đơn lẻ)
    def _convert_component(raw_number: str, tail_segment: str, is_usd_context: bool) -> float | None:
        try:
            local_tail = (tail_segment or '').lower().strip()
            # Nếu có đơn vị k/m/b hoặc các biến thể triệu/tr/mil => cho phép số thập phân (ví dụ: 2.2k)
            has_scale_unit = (
                re.match(r'^(k|m|b)\b', local_tail) is not None
                or local_tail.startswith('triệu')
                or local_tail.startswith('tr')
                or local_tail.startswith('mil')
            )

            if has_scale_unit:
                # Giữ dấu thập phân '.', loại bỏ dấu phẩy ngăn cách nghìn
                cleaned = raw_number.replace(',', '')
                # Trường hợp '1.500' với đơn vị k/m/b hiếm, nhưng nếu có thì coi '.' là thập phân hợp lệ
                base_val = float(cleaned)
            else:
                # Không có đơn vị mở rộng => coi '.' và ',' là phân cách nghìn
                cleaned = raw_number.replace('.', '').replace(',', '')
                if not cleaned.isdigit():
                    return None
                base_val = float(cleaned)
        except Exception:
            return None

        # Xác định unit cục bộ
        local_tail = (tail_segment or '').lower()
        multiplier_local = 1
        # Phát hiện k/m/b viết tắt đứng liền sau số (vd: 2.2k, 3m)
        # hoặc các từ khóa triệu/tr/b
        if re.match(r'^k\b', local_tail):
            multiplier_local = 1000 if is_usd_context else 1000  # cho USD sẽ nhân sau bằng usd_to_vnd
        elif re.match(r'^m\b', local_tail) or local_tail.startswith('triệu') or local_tail.startswith('tr') or local_tail.startswith('mil'):
            multiplier_local = 1000000
        elif re.match(r'^b\b', local_tail):
            multiplier_local = 1000000000

        value = base_val * multiplier_local
        if is_usd_context:
            value *= usd_to_vnd
        return value

    # (Sẽ bổ sung regex 'from' / 'up to' phía trên khi hoàn thiện các bước tiếp theo)

    # Làm sạch chuỗi
    salary_clean = re.sub(r'\(.*\)|net|gross|\/tháng|\+.*|đ', '', salary_lower).strip()

    is_yearly = '/year' in salary_clean
    salary_clean = salary_clean.replace('/year', '').strip()

    # SPECIAL: Annual USD pattern like 'total $60k/year' hoặc '$60k/year'
    annual_pattern = re.compile(r'^(?:total\s+)?\$?([0-9][0-9\.,]*)(k)?(?:\s*usd)?$')
    if is_yearly:
        annual_match = annual_pattern.match(salary_clean)
        if annual_match:
            raw_num = annual_match.group(1)
            has_k = annual_match.group(2) is not None
            num_clean = raw_num.replace('.', '').replace(',', '')
            if num_clean.isdigit():
                annual_usd = float(num_clean)
                if has_k:
                    annual_usd *= 1000
                monthly_vnd = int((annual_usd * usd_to_vnd) / 12)
                return monthly_vnd, monthly_vnd, monthly_vnd

    # Regex bắt sớm pattern 'From <number><optional separators><unit><optional currency>'
    # Ví dụ: From 10.000.000 VND ; From 35.000.000 (gross) ; From $1300 ; From 2.2k ; From 45tr
    from_pattern = re.compile(r'^from\s+([0-9][0-9\.,]*)(\s*[kmb]|\s*triệu|\s*tr|\s*mil|\s*b)?(?:\s*(usd|vnd))?')
    match_from = from_pattern.match(salary_clean)
    if match_from:
        number_part = match_from.group(1)
        unit_part = (match_from.group(2) or '').strip()
        currency_part = (match_from.group(3) or '').strip()
        is_usd_context = 'usd' in currency_part or '$' in original_str.lower()
        conv_val = _convert_component(number_part, unit_part, is_usd_context)
        if conv_val is not None:
            # Điều chỉnh theo năm nếu có '/year'
            if is_yearly:
                conv_val = int(conv_val / 12)
            min_salary = conv_val
            max_salary = None
            avg_salary = min_salary
            return min_salary, max_salary, avg_salary

    # Regex cho 'Up to <number><unit><currency>'
    upto_pattern = re.compile(r'^up\s*to\s+([0-9][0-9\.,]*)(\s*[kmb]|\s*triệu|\s*tr|\s*mil|\s*b)?(?:\s*(usd|vnd))?')
    match_upto = upto_pattern.match(salary_clean)
    if match_upto:
        number_part = match_upto.group(1)
        unit_part = (match_upto.group(2) or '').strip()
        currency_part = (match_upto.group(3) or '').strip()
        is_usd_context = 'usd' in currency_part or '$' in original_str.lower()
        # Heuristic: nếu dùng dạng '2k', '2.2k' mà không ghi vnd/vnđ thì coi là USD nghìn
        if not is_usd_context and unit_part == 'k' and not any(tok in salary_clean for tok in ['vnd', 'vnđ']):
            is_usd_context = True
        conv_val = _convert_component(number_part, unit_part, is_usd_context)
        # Nếu là VND (ngầm định hoặc tường minh) và nhỏ hơn 1,000,000 thì coi là không hợp lệ
        if conv_val is not None and not is_usd_context and conv_val < 1_000_000:
            return None, None, None
        if conv_val is not None:
            # Điều chỉnh theo năm nếu có '/year'
            if is_yearly:
                conv_val = int(conv_val / 12)
            min_salary = None
            max_salary = conv_val
            avg_salary = max_salary
            return min_salary, max_salary, avg_salary

    # Tìm tất cả các số trong chuỗi
    numbers = re.findall(r'(\d[\d\.,]*)', salary_clean)
    
    cleaned_numbers = []
    for num in numbers:
        num_clean = num.replace('.', '').replace(',', '')
        if num_clean.isdigit():
            cleaned_numbers.append(float(num_clean))

    numbers = cleaned_numbers

    # Xác định đơn vị tiền tệ và áp dụng hệ số nhân
    multiplier = 1
    is_usd = 'usd' in salary_clean or '$' in salary_clean

    if not is_usd: # Giả định là VND nếu không phải USD
        if 'b' in salary_clean: # Tỷ
            multiplier = 1000000000
        elif any(unit in salary_clean for unit in ['m', 'triệu', 'tr', 'mil']):
             multiplier = 1000000
    elif 'k' in salary_clean: # USD
        multiplier = 1000

    numbers = [n * multiplier for n in numbers]
    
    if is_usd:
        numbers = [n * usd_to_vnd for n in numbers]
    
    # Trích xuất min/max (mặc định)
    if 'up to' in salary_clean or 'upto' in salary_clean:
        if numbers:
            max_salary = numbers[0]
            # Theo yêu cầu mới: Min Lương = NaN (None) thay vì 0 cho các mẫu Up to
            min_salary = None
            # Nếu ngữ cảnh là VND (không có USD) và max < 1,000,000 thì vô hiệu
            if ('usd' not in salary_clean and '$' not in salary_clean) and max_salary is not None and max_salary < 1_000_000:
                return None, None, None
    elif 'from' in salary_clean or 'min' in salary_clean:
        if numbers:
            min_salary = numbers[0]
            max_salary = None
            # Nếu ngữ cảnh là VND (không có USD) và min < 1,000,000 thì vô hiệu
            if ('usd' not in salary_clean and '$' not in salary_clean) and min_salary is not None and min_salary < 1_000_000:
                return None, None, None
    elif len(numbers) == 2:
        min_salary, max_salary = sorted(numbers)
    elif len(numbers) == 1:
        min_salary = max_salary = numbers[0]
    
    # ------------------ SPECIAL CASE OVERRIDES THEO YÊU CẦU ------------------
    # Ghi chú: xử lý sau khi parse cơ bản nhưng trước khi tính trung bình
    # so khớp ở dạng lower để tránh sai khác hoa/thường.

    lower_trimmed = salary_lower.strip()

    # 1. "Up to $3200" => Min = None, Max = 83,200,000 (override theo usd_to_vnd=26k * 3200)
    if lower_trimmed == 'up to $3200':
        min_salary = None
        max_salary = 83200000

    # 2. "Up to 40,000,000 vnđ" => Min = None, Max = 40,000,000 (đã được logic chung, chỉ đảm bảo không bị 0)
    if lower_trimmed in ['up to 40,000,000 vnđ', 'up to 40,000,000 vnd', 'up to 40,000,000 vnđ.']:
        min_salary = None
        max_salary = 40000000

    # 3. Dải chuẩn (đã hoạt động sẵn): "15,000,000đ - 30,000,000đ" => giữ nguyên
    # 4. "45tr - 50tr (gross)" => đã hoạt động sẵn (đã loại 'gross')
    # 5. "25,000,000 - 40,000,000đ" => đã hoạt động sẵn

    # 6. "Up to 30 months/year" => cả hai None
    if lower_trimmed == 'up to 30 months/year':
        min_salary = None
        max_salary = None

    

    # 8. "30 triệu - 47 triệu net" 
    if lower_trimmed == '30 triệu - 47 triệu net':
        min_salary = 30000000
        max_salary = 47000000

    # 9. "Up to 1b vnd/year" => đã xử lý ở nhánh 'up to' và chia 12 ngay lập tức nếu có '/year'
    # (Giữ ghi chú để tham chiếu)

    # 10. "700 USD to 1.500 USD" => để logic chung xử lý (đã đúng). Chuẩn hóa nếu cần.
    if lower_trimmed == '700 usd to 1.500 usd':
        # Đảm bảo đúng nếu logic trước đó thay đổi trong tương lai
        min_salary = 700 * usd_to_vnd
        max_salary = 1500 * usd_to_vnd

    # 10b. "Up to 2.2k" => coi là USD (2.2 * 1000 USD)
    if lower_trimmed == 'up to 2.2k':
        min_salary = None
        max_salary = int(2200 * usd_to_vnd)

    # 10c. "Up to 2k" => coi là USD (2 * 1000 USD)
    if lower_trimmed == 'up to 2k':
        min_salary = None
        max_salary = int(2000 * usd_to_vnd)

    # Trường hợp đặc biệt ban đầu: "Up to 1.500 VND" (giữ nếu vẫn muốn)
    # Bỏ xử lý 'Up to 1.500 VND' vì < 1,000,000 VND không hợp lệ theo yêu cầu mới
    if lower_trimmed == 'up to 1.500 vnd':
        return None, None, None
        
    # Xử lý lương theo năm (trừ khi đã override đặc biệt áp giá trị tháng cụ thể)
    if is_yearly:
        if min_salary is not None:
            min_salary /= 12
        if max_salary is not None:
            max_salary /= 12
        # Làm tròn xuống integer VND cho gọn
        if min_salary is not None:
            min_salary = int(min_salary)
        if max_salary is not None:
            max_salary = int(max_salary)

    # Tính lương trung bình
    avg_salary = None
    if min_salary is not None and max_salary is not None:
        avg_salary = (min_salary + max_salary) / 2
    elif min_salary is not None:
        avg_salary = min_salary
    elif max_salary is not None:
        avg_salary = max_salary
    
    return min_salary, max_salary, avg_salary

if __name__ == '__main__':
    # lấy từ file combined_jobs_ordered.csv
    df = pd.read_csv('combined_jobs_ordered.csv')

    # Áp dụng hàm xử lý cho cột 'Lương'
    df['Min Lương'], df['Max Lương'], df['Average Lương'] = zip(*df['Lương'].apply(process_salary))

    # Lưu kết quả ra file CSV
    output_filename = 'final_cleaned.csv'
    df.to_csv(output_filename, encoding='utf-8-sig', index=False)

    print(f"Đã xử lý xong và lưu vào file '{output_filename}'.")
    print("\n5 dòng đầu của kết quả:")
    print(df.head().to_string())