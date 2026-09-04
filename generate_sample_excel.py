"""
Script tạo file Excel mẫu chứa bình luận khách hàng đa dạng.
"""
import sys
import io

# Đảm bảo UTF-8 cho console Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os

sample_data = [
    {
        "Mã Đơn": "ORD_1001",
        "Khách Hàng": "Nguyễn Hoàng Nam",
        "Đánh Giá Sao": 5,
        "Bình Luận Đánh Giá": "Shop ơi GIAO HÀNG chậm quá :(( nhưng chất lượng ổn áp nha!!!"
    },
    {
        "Mã Đơn": "ORD_1002",
        "Khách Hàng": "Trần Thu Hà",
        "Đánh Giá Sao": 5,
        "Bình Luận Đánh Giá": "Đóng gói hàng cẩn thận, shipper thân thiện dễ thương ❤️❤️❤️ Cho shop 5 sao nhé ^^"
    },
    {
        "Mã Đơn": "ORD_1003",
        "Khách Hàng": "David Miller",
        "Đánh Giá Sao": 5,
        "Bình Luận Đánh Giá": "Excellent product quality and very fast shipping! 10/10 recommend."
    },
    {
        "Mã Đơn": "ORD_1004",
        "Khách Hàng": "Lê Minh Tuấn",
        "Đánh Giá Sao": 1,
        "Bình Luận Đánh Giá": "Hàng giả nhái kém chất lượng, đừng ai mua nha lừa đảo đấy 😡😡😡"
    },
    {
        "Mã Đơn": "ORD_1005",
        "Khách Hàng": "Phạm Thị Lan",
        "Đánh Giá Sao": 4,
        "Bình Luận Đánh Giá": "Vải mát mặc thoải mái, nhưng giao màu hơi nhạt hơn trong hình quảng cáo một chút :3"
    },
    {
        "Mã Đơn": "ORD_1006",
        "Khách Hàng": "John Doe",
        "Đánh Giá Sao": 2,
        "Bình Luận Đánh Giá": "The item was damaged during shipping. Bad packaging."
    },
    {
        "Mã Đơn": "ORD_1007",
        "Khách Hàng": "Vũ Anh Đức",
        "Đánh Giá Sao": 5,
        "Bình Luận Đánh Giá": "Giá rẻ mà xài cực kỳ êm ru, giao hàng hỏa tốc trong 2h siêu tiện lợi <3 <3"
    }
]

df = pd.DataFrame(sample_data)
output_file = os.path.join(os.path.dirname(__file__), "sample_reviews.xlsx")
df.to_excel(output_file, index=False)
print(f"[*] Da tao file Excel mau thanh cong: {output_file}")
