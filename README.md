# ProjectSpark: Nền Tảng Phân Tích Dữ Liệu GitHub (Big Data)

Chào mừng bạn đến với **ProjectSpark**, một giải pháp toàn diện để xử lý và phân tích dữ liệu lớn (Big Data) từ GitHub Archive sử dụng sức mạnh của **Apache Spark** kết hợp với giao diện trực quan **Web Dashboard**.

---

## 🚀 Giới Thiệu

Dự án này được xây dựng nhằm giải quyết bài toán xử lý các file log JSON lồng nhau phức tạp từ GitHub. Hệ thống cho phép người dùng:
1.  **Nạp dữ liệu thô (Raw Data)**: Upload file `.json.gz` hoặc `.json`.
2.  **Xử lý (ETL)**: Kích hoạt Spark Job để làm phẳng (flatten) dữ liệu và trích xuất thông tin quan trọng.
3.  **Trực quan hóa**: Xem các biểu đồ và thống kê trên giao diện Web Dashboard hiện đại (Dark Mode).

## ✨ Tính Năng Nổi Bật

*   **Xử Lý Big Data**: Sử dụng Apache Spark để xử lý lượng lớn dữ liệu commit, push event.
*   **Giao Diện Hiện Đại**: Dashboard Web (Flask + Bootstrap 5 + Chart.js) với chế độ Dark Theme cao cấp.
*   **Data Manager Chất Lượng**:
    *   Upload file trực tiếp trên web.
    *   Kích hoạt Spark Job chỉ với 1 cú click.
    *   Quản lý và chọn lựa giữa các tập dữ liệu đã xử lý.
*   **Data Explorer**: Xem dữ liệu thô dạng bảng (DataTable) với khả năng tìm kiếm và lọc mạnh mẽ.
*   **Dockerized**: Môi trường Spark và Jupyter được đóng gói trong Docker, đảm bảo tính nhất quán.

## 📂 Cấu Trúc Dự Án

*   `src/`: Mã nguồn xử lý dữ liệu (Spark Notebooks & Scripts).
    *   `etl_job.py`: Script Python chính để chạy Spark ETL.
*   `web_app/`: Ứng dụng Web Dashboard.
    *   `app.py`: Backend (Flask).
    *   `templates/index.html`: Giao diện người dùng.
*   `data/`: Kho chứa dữ liệu.
    *   `raw/`: Dữ liệu đầu vào chưa xử lý.
    *   `processed/`: Dữ liệu CSV sau khi Spark xử lý xong.
*   `AI_help/`: Tài liệu hỗ trợ (dành cho dev).
*   `Present/`: Tài liệu báo cáo & slide.

## 🛠 Hướng Dẫn Cài Đặt & Chạy

### 1. Khởi động Môi Trường
Đảm bảo bạn đã start các container Docker:
```bash
cd /home/ubuntu/spark
./start-spark.sh # Script khởi động (nếu có) hoặc docker-compose up -d
```

### 2. Chạy Web Dashboard
D dashboard là trung tâm điều khiển của hệ thống.
Chạy lênh sau trong terminal:
```bash
python3 /home/ubuntu/spark/ProjectSpark/web_app/app.py
```
*   Server sẽ khởi chạy tại: `http://localhost:5000` (hoặc IP Cloud Server).

### 3. Sử dụng
1.  Truy cập Web Dashboard.
2.  Vào tab **Data Manager**.
3.  **Upload** file JSON log từ GitHub Archive.
4.  Bấm nút **⚡ Run Spark** để hệ thống tự động gọi Docker xử lý dữ liệu.
5.  Sau khi chạy xong, bấm **✅ Select** để hiển thị dữ liệu lên Dashboard.
6.  Quay lại tab **Dashboard** để xem biểu đồ phân tích.

---

## 🔧 Công Nghệ Sử Dụng
*   **Core**: Apache Spark 3.5.0, PySpark.
*   **Backend**: Python, Flask, Pandas.
*   **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript (Chart.js, DataTables).
*   **Infra**: Docker, Ubuntu Linux.

---
*Created by ProjectSpark Team*
