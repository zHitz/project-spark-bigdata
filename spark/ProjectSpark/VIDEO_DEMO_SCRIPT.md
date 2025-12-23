# HƯỚNG DẪN CHI TIẾT CÁCH THỰC HIỆN & KỊCH BẢN QUAY VIDEO DEMO
**Đề tài 25**: Phân tích dữ liệu JSON lồng nhau phức tạp với Apache Spark

Tài liệu này hướng dẫn từng bước (Step-by-step) để bạn thực hiện và quay video demo nộp cho giảng viên.

---

## PHẦN 1: CHUẨN BỊ (Làm trước khi quay)

1.  **Kiểm tra dữ liệu**:
    - Đảm bảo file `2015-01-01-15.json` đã nằm trong thư mục `ProjectSpark/data/raw`.
2.  **Reset môi trường** (để video trông như làm từ đầu):
    - Xóa các file kết quả cũ trong `ProjectSpark/data/processed` (nếu có).
    - Chọn *Restart Kernel and Clear All Outputs* trong các notebook để xóa kết quả chạy trước đó.

---

## PHẦN 2: KỊCH BẢN QUAY VIDEO (Bắt đầu quay từ đây)

### Bước 1: Khởi động hệ thống (0:00 - 0:30)
*Mở Terminal (màn hình dòng lệnh)*

1.  **Gõ lệnh khởi động**:
    ```bash
    cd /home/ubuntu
    docker compose up -d
    ```
2.  **Giải thích**: "Đầu tiên, nhóm em khởi động hệ thống Big Data gồm Spark Master, Spark Worker và Jupyter Notebook chạy trên Docker."
3.  **Kiểm tra trạng thái**:
    ```bash
    docker ps
    ```
    -> Chỉ vào màn hình thấy 3 container đang chạy (Up).

### Bước 2: Truy cập môi trường phát triển (0:30 - 1:00)
*Mở trình duyệt web (Chrome/Firefox)*

1.  Truy cập: `http://localhost:8888` (hoặc IP máy ảo).
2.  Nhập Token (nếu bị hỏi).
3.  Vào thư mục: `work` -> `ProjectSpark`.
4.  **Giới thiệu cấu trúc**: "Đây là cấu trúc dự án của nhóm, gồm thư mục `data` chứa dữ liệu thô và `src` chứa mã nguồn xử lý."

### Bước 3: Ingest & Khám phá dữ liệu (1:00 - 2:30)
*Mở notebook `src/1_ingest_and_explore.ipynb`*

1.  **Chạy Cell 1 & 2** (Khởi tạo Spark):
    - "Nhóm sử dụng SparkSession để khởi tạo ứng dụng."
2.  **Chạy Cell "Read JSON"**:
    - "Dữ liệu đầu vào là file GitHub Archive định dạng JSON."
3.  **Chạy Cell "Print Schema"**:
    - **Quan trọng**: Dừng lại ở đây và chỉ vào cấu trúc cây.
    - "Như thầy/cô thấy, dữ liệu có cấu trúc lồng nhau rất phức tạp (Nested Data). Ví dụ: `actor` là struct, `payload.commits` là một mảng (Array) chứa nhiều object con."
4.  **Chạy Cell hiển thị dữ liệu**:
    - Cho thấy dữ liệu thô ban đầu khó đọc như thế nào.

### Bước 4: Xử lý làm phẳng dữ liệu - Flatten (2:30 - 4:30)
*Mở notebook `src/2_flatten_data.ipynb`* -> **Đây là phần kỹ thuật quan trọng nhất!**

1.  **Chạy Cell load dữ liệu**.
2.  **Giải thích kỹ thuật Explode**:
    - Kéo xuống đoạn code `explode(col("payload.commits"))`.
    - **Nói**: "Để xử lý mảng commits, nhóm sử dụng hàm `explode` của Spark SQL. Hàm này sẽ tách từng phần tử trong mảng thành các dòng riêng biệt, biến dữ liệu phân cấp thành dạng bảng phẳng."
3.  **Giải thích kỹ thuật Truy xuất lồng nhau**:
    - Chỉ vào các dòng `col("commit.author.name")`.
    - "Sau khi explode, nhóm truy xuất sâu vào các tầng dữ liệu thứ 4, thứ 5 để lấy thông tin tác giả, message commit..."
4.  **Chạy Cell lưu file (Write CSV/Parquet)**:
    - "Cuối cùng, dữ liệu sạch được lưu xuống định dạng CSV để phục vụ báo cáo."
    - Chờ code chạy xong báo "Data saved successfully!".

### Bước 5: Kiểm tra kết quả & Dashboard (4:30 - 5:30)
*Mở notebook `src/3_analyze_dashboard.ipynb`*

1.  **Load dữ liệu đã xử lý**:
    - Chạy cell đọc file Parquet/CSV vừa tạo.
2.  **Show Top Contributors**:
    - Chạy cell thống kê.
    - "Từ dữ liệu đã làm phẳng, nhóm dễ dàng dùng câu lệnh SQL/DataFrame API để tìm ra top 10 lập trình viên hoạt động tích cực nhất."
3.  **Show Top Repositories**:
    - Chạy cell tiếp theo.
    - "Và top 10 dự án mã nguồn mở sôi động nhất trong thời điểm đó."

### Bước 6: Tổng kết & Kết thúc (5:30 - 6:00)
1.  **Mở folder** `data/processed`:
    - Chỉ vào file `github_commits_flat.csv`.
    - Download file này về (hoặc mở lên xem nhanh) để chứng minh output là thật.
2.  **Kết lời**: "Như vậy nhóm đã hoàn thành việc xây dựng pipeline xử lý dữ liệu JSON phức tạp với Spark. Cảm ơn thầy cô đã theo dõi."

---

## PHẦN 3: CÁC FILE CẦN NỘP

Dựa trên quá trình trên, bạn sẽ có đủ các file để nộp:
1.  **Source Code**: Thư mục `src/` (3 file .ipynb).
2.  **Kết quả**: File `data/processed/github_commits_flat.csv`.
3.  **Video**: File quay màn hình làm theo kịch bản trên.
