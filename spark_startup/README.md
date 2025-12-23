# Hướng Dẫn Cài Đặt Spark & Jupyter với Docker

Tài liệu này hướng dẫn cách thiết lập, cấu hình và sử dụng môi trường Apache Spark tích hợp với Jupyter Notebook bằng Docker Compose.

## 1. Yêu Cầu
- **Docker** và **Docker Compose** đã được cài đặt trên máy.

## 2. Cài Đặt và Khởi Chạy
Bạn chỉ cần chạy một lệnh duy nhất để khởi động toàn bộ hệ thống:

```bash
docker compose up -d
```

Để dừng hệ thống:
```bash
docker compose down
```

## 3. Cách Hoạt Động
Hệ thống bao gồm 3 dịch vụ chính:
1.  **spark-master**: Quản lý cluster Spark.
2.  **spark-worker**: Thực thi các tác vụ tính toán (Executor).
3.  **jupyter**: Môi trường lập trình Notebook (Driver).

**Điểm đặc biệt trong cấu hình này:**
- **Đồng bộ phiên bản**: Tất cả các dịch vụ (Master, Worker, Jupyter) đều sử dụng cùng một Docker image (`jupyter/pyspark-notebook:spark-3.5.0`). Điều này đảm bảo phiên bản Python (3.11) và các thư viện hoàn toàn tương thích, tránh lỗi "Python version mismatch".
- **Tự động khởi tạo**: Khi bạn mở Notebook, một script khởi động (`00-start-spark.py`) sẽ tự động chạy để tạo sẵn biến `spark` (SparkSession) kết nối tới Master. Bạn không cần phải cấu hình thủ công mỗi khi code.
- **Quyền hạn**: Dịch vụ Jupyter được cấu hình để tự động sửa quyền truy cập thư mục `.ipython`, đảm bảo không gặp lỗi "Permission denied".

## 4. Truy Cập Sử Dụng
Sau khi khởi chạy thành công:

### Truy cập Jupyter Notebook
1.  Xem token đăng nhập bằng lệnh:
    ```bash
    docker logs jupyter-notebook
    ```
    Tìm dòng có dạng: `http://127.0.0.1:8888/lab?token=...`

2.  Mở trình duyệt:
    - Nếu chạy trên máy cá nhân: Truy cập `http://localhost:8888`
    - Nếu truy cập từ xa (ví dụ: máy khác kết nối tới server): Truy cập `http://<IP-Của-Server>:8888`

### Sử dụng Spark
Trong Notebook, bạn có thể sử dụng biến `spark` ngay lập tức mà không cần `import` hay cấu hình gì thêm.

Ví dụ kiểm tra nhanh:
```python
# Biến 'spark' đã có sẵn
print(spark.version)

# Tạo thử một DataFrame
df = spark.createDataFrame([(1, "A"), (2, "B")], ["ID", "Tên"])
df.show()
```

## 5. Cấu Hình Chi Tiết (`docker-compose.yml`)
Nếu bạn muốn thay đổi cấu hình, hãy chỉnh sửa file `docker-compose.yml`:

- **Cấu hình tài nguyên**:
    - `SPARK_WORKER_MEMORY=1G`: Giới hạn RAM cho Worker.
    - `spark.executor.memory=1g`: Cấu hình RAM cho mỗi Executor trong `PYSPARK_SUBMIT_ARGS`.

- **Cổng kết nối (Ports)**:
    - `8888`: Jupyter Notebook UI.
    - `8080`: Spark Master UI (để theo dõi trạng thái cluster).
    - `7077`: Cổng kết nối nội bộ của Spark Master.

- **Dữ liệu (Volumes)**:
    - `./spark:/home/jovyan/work`: Các file notebook của bạn sẽ được lưu trong thư mục `spark` trên máy thật, giúp dữ liệu không bị mất khi xóa container.
