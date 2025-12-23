# HƯỚNG DẪN THỰC HIỆN DEMO
**Mục tiêu**: Thực hiện thao tác Demo dự án "ProjectSpark" trên giao diện Web Jupyter Lab.

## 1. Môi trường & Ngữ cảnh (Context)
- **Hệ thống**: Jupyter Lab chạy trên Docker container.
- **URL truy cập**: `http://192.168.1.12:8888` (hoặc `http://localhost:8888` nếu map port).
- **Authentication Token**:
    - Token hiện tại: `37d150a32566e4908d4b6b88f1e2b6e20fc192f5e9b0beeb`
    - *Lưu ý*: Nếu Token không đúng, hãy yêu cầu người dùng chạy lệnh: `docker logs jupyter-notebook` trên server để lấy token mới.

## 2. Quy trình thực hiện (Step-by-Step Action Plan)

### Bước 1: Đăng nhập
1.  Truy cập URL: `http://192.168.1.12:8888/lab?token=37d150a32566e4908d4b6b88f1e2b6e20fc192f5e9b0beeb`
2.  Chờ giao diện Jupyter Lab tải xong (khoảng 5-10 giây).

### Bước 2: Điều hướng đến Source Code
1.  Ở thanh bên trái (File Browser), click đúp vào thư mục **`work`**.
2.  Click đúp vào thư mục **`ProjectSpark`**.
3.  Click đúp vào thư mục **`src`**.
    - *Kiểm tra*: Bạn sẽ thấy 3 file notebook: `1_ingest...`, `2_flatten...`, `3_analyze...`.

### Bước 3: Chạy Notebook 1 - Ingest Data
1.  Click đúp mở file **`1_ingest_and_explore.ipynb`**.
2.  Trên thanh công cụ bên trên, nhấn menu **Run** -> Chọn **Run All Cells**.
3.  **Hành động cuộn (Scroll)**:
    - Cuộn xuống từ từ để hiển thị kết quả.
    - Dừng lại 3 giây ở cell `df_raw.printSchema()` để hiển thị cấu trúc cây (tree structure).
    - Cuộn xuống cuối cùng để thấy bảng dữ liệu mẫu.

### Bước 4: Chạy Notebook 2 - Flatten Data (Quan trọng nhất)
1.  Click đúp mở file **`2_flatten_data.ipynb`**.
2.  Nhấn menu **Run** -> **Run All Cells**.
3.  **Hành động cuộn (Scroll)**:
    - Cuộn đến cell Step 1: Dừng 3 giây để hiển thị code `explode(col("payload.commits"))`.
    - Cuộn đến cell Step 2: Dừng 3 giây để hiển thị code `col("commit.author.name")`.
    - Cuộn xuống cuối cùng, đợi dòng chữ "Data saved successfully!" xuất hiện.

### Bước 5: Chạy Notebook 3 - Dashboard
1.  Click đúp mở file **`3_analyze_dashboard.ipynb`**.
2.  Nhấn menu **Run** -> **Run All Cells**.
3.  **Hành động cuộn (Scroll)**:
    - Cuộn xuống để hiển thị bảng **Insight 1: Top 10 Contributors**.
    - Cuộn tiếp để hiển thị bảng **Insight 2: Top 10 Repositories**.

### Bước 6: Kiểm tra kết quả Output
1.  Ở thanh bên trái, click vào icon thư mục cha (Root) hoặc click vào breadcrumb để quay lại `ProjectSpark`.
2.  Vào thư mục **`data`** -> **`processed`**.
3.  Chỉ vào file **`github_commits_flat.csv`** (có thể click đúp mở ra để chứng minh file tồn tại).

### Bước 7: Demo Web Platform (Nâng Cao)
1.  **Quan trọng**: Mở Terminal, chạy `python3 /home/ubuntu/spark/ProjectSpark/web_app/app.py`.
2.  Truy cập: `http://localhost:5000`.
3.  **Tab 1 - Dashboard**: Show biểu đồ đẹp (Top Orgs, Email Domains...).
4.  **Tab 2 - Data Manager**:
    - Click tab **"Data Manager"**.
    - Chỉ vào file `2015-02-01-15.json.gz` trong danh sách.
    - Bấm nút **⚡ Run Spark Job** (Giả vờ bấm hoặc bấm thật nếu muốn demo live processing).
    - Giải thích: "Hệ thống cho phép chọn source log bất kỳ để xử lý."
5.  **Tab 3 - Data Explorer**:
    - Click tab **"Data Explorer"**.
    - Show bảng dữ liệu chi tiết (Excel-like view).
    - Thử nhập vào ô Search (ví dụ: "gmail") để lọc dữ liệu realtime.

## 3. Lưu ý
- Nếu gặp lỗi "Kernel not ready" hoặc "Connection failed", hãy thử Refresh (F5) trang web và làm lại.
