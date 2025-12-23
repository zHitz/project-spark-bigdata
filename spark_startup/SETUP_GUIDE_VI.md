# Tài Liệu Triển Khai Hệ Thống Apache Spark Kết Hợp Jupyter Notebook

**Phiên bản:** 1.0  
**Tác giả:** Hitz  
**Ngày:** 11/12/2025

---

## 1. Giới Thiệu Chung
Tài liệu này mô tả chi tiết quy trình thiết lập, cấu hình và nguyên lý hoạt động của môi trường xử lý dữ liệu lớn (Big Data) sử dụng **Apache Spark** chạy trên nền tảng **Docker**. Môi trường này tích hợp sẵn **Jupyter Notebook** để phục vụ việc phân tích dữ liệu và phát triển thuật toán một cách trực quan.

### Mục Đích
- Quy chuẩn hóa môi trường phát triển (Development Environment).
- Giải quyết triệt để các vấn đề tương thích phiên bản (Dependency Hell).
- Hướng dẫn chi tiết cho đội ngũ kỹ thuật về cách vận hành và xử lý sự cố.

---

## 2. Kiến Trúc Hệ Thống

Hệ thống được thiết kế theo mô hình **Master-Slave** chạy trên các container độc lập:

1.  **Spark Master (Quản lý):**
    - Đóng vai trò điều phối tài nguyên của cụm (cluster).
    - Lắng nghe yêu cầu từ client và phân phối công việc cho các Worker.
    - Cổng giao tiếp: `7077` (nội bộ), `8080` (Web UI).

2.  **Spark Worker (Thực thi):**
    - Chịu trách nhiệm thực hiện các tác vụ (Task) tính toán thực tế.
    - Báo cáo trạng thái và kết quả về Master.

3.  **Jupyter Notebook (Client/Driver):**
    - Là nơi người dùng viết code (Python/PySpark).
    - Đóng vai trò là **Driver Program** trong kiến trúc Spark. Driver chứa `SparkContext`, chịu trách nhiệm gửi code tới Cluster để chạy.

---

## 3. Chi Tiết Triển Khai & Giải Thích Kỹ Thuật

Chúng ta sử dụng **Docker Compose** để đóng gói toàn bộ hệ thống. Dưới đây là các quyết định kỹ thuật quan trọng và lý do tại sao phải làm như vậy.

### 3.1. Đồng Bộ Hóa Môi Trường (Critical)
**Vấn đề:** 
Một lỗi rất phổ biến khi làm việc với Spark là `Python Version Mismatch`. Nếu máy tính chạy code (Driver) dùng Python 3.11 nhưng Worker dùng Python 3.8, chương trình sẽ báo lỗi khi Worker cố gắng giải mã (deserialize) các hàm được gửi từ Driver.

**Giải pháp:**
Chúng ta ép buộc **tất cả các dịch vụ** (Master, Worker, Jupyter) sử dụng **chung một Docker image**:
`jupyter/pyspark-notebook:spark-3.5.0`

> **Tại sao?** Điều này đảm bảo tuyệt đối rằng phiên bản Python, phiên bản Spark, và các thư viện trong hệ điều hành (OS libraries) là giống hệt nhau ở mọi nơi.

### 3.2. Cấu Hình `docker-compose.yml`

File cấu hình chính của hệ thống.

```yaml
services:
  # --- SPARK MASTER ---
  spark-master:
    image: jupyter/pyspark-notebook:spark-3.5.0
    container_name: spark-master
    user: root  # Chạy quyền root để tránh lỗi quyền ghi file log/work
    command: /usr/local/spark/bin/spark-class org.apache.spark.deploy.master.Master
    ports:
      - "8080:8080" # Web UI để xem trạng thái Cluster
      - "7077:7077" # Cổng kết nối quan trọng nhất
    volumes:
      - /home/ubuntu/spark:/home/jovyan/work

  # --- SPARK WORKER ---
  spark-worker:
    image: jupyter/pyspark-notebook:spark-3.5.0
    container_name: spark-worker
    user: root
    # Lệnh khởi động Worker và trỏ về Master
    command: /usr/local/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://spark-master:7077
    environment:
      - SPARK_WORKER_MEMORY=1G # Giới hạn RAM
    depends_on:
      - spark-master

  # --- JUPYTER NOTEBOOK (CLIENT) ---
  jupyter:
    image: jupyter/pyspark-notebook:spark-3.5.0
    container_name: jupyter-notebook
    # Fix quyền thư mục .ipython trước khi chạy để Startup Script hoạt động
    command: bash -c "chown -R 1000:100 /home/jovyan/.ipython && /usr/local/bin/start-notebook.sh"
    ports:
      - "8888:8888"
    volumes:
      - /home/ubuntu/spark:/home/jovyan/work
      # Mount thư mục chứa script khởi động tự động
      - /home/ubuntu/jupyter_startup:/home/jovyan/.ipython/profile_default/startup
    environment:
      # Định nghĩa tham số để PySpark tự động biết kết nối vào đâu
      - PYSPARK_SUBMIT_ARGS=--master spark://spark-master:7077 --conf spark.executor.memory=1g pyspark-shell
      # Thêm Py4j vào PYTHONPATH để Python tìm thấy thư viện cầu nối Java
      - PYTHONPATH=/usr/local/spark/python:/usr/local/spark/python/lib/py4j-0.10.9.7-src.zip
```

### 3.3. Tự Động Hóa Kết Nối (Automated Startup)
**Vấn đề:** 
Thông thường, mỗi khi mở Notebook, người dùng phải chạy một đoạn code dài dòng để import `SparkSession`, cấu hình Master URL...

**Giải pháp:**
Sử dụng tính năng **IPython Startup**. Bất kỳ file `.py` nào đặt trong thư mục `~/.ipython/profile_default/startup/` sẽ được chạy tự động khi Kernel khởi động.

Chúng ta đã tạo file `00-start-spark.py`:
1.  Lấy thông tin Master URL từ biến môi trường.
2.  Tự động khởi tạo đối tượng `spark` và `sc`.
3.  Người dùng mở lên là dùng được ngay.

---

## 4. Hướng Dẫn Vận Hành

### Bước 1: Khởi động hệ thống
Di chuyển vào thư mục chứa `docker-compose.yml` và chạy:
```bash
docker compose up -d
```
Docker sẽ tải (pull) các image cần thiết và khởi động 3 container.

### Bước 2: Lấy thông tin đăng nhập
Vì lý do bảo mật, Jupyter yêu cầu Token. Chạy lệnh sau để xem:
```bash
docker logs jupyter-notebook
```
Bạn sẽ thấy đường dẫn có dạng:
`http://127.0.0.1:8888/lab?token=a740b...`

### Bước 3: Truy cập
- Trên máy Server/Local: Vào `http://localhost:8888`
- Từ máy khác trong mạng LAN: Vào `http://192.168.1.12:8888` (thay IP tương ứng).

---

## 5. Xử Lý Sự Cố Thường Gặp (Troubleshooting)

### 5.1. Lỗi "Spark not defined"
- **Nguyên nhân:** Script khởi động `00-start-spark.py` không chạy được. Thường do Jupyter không có quyền ghi vào thư mục cấu hình `.ipython`.
- **Cách xử lý:** Kiểm tra lệnh `command` của service `jupyter` trong docker-compose. Nó phải có bước `chown` quyền cho thư mục `.ipython`.

### 5.2. Lỗi Python Version Mismatch
- **Hiện tượng:** Job chạy bị lỗi, log báo `Exception: Python in worker has different version 3.8 than that in driver 3.11`.
- **Cách xử lý:** Đảm bảo `spark-master`, `spark-worker` và `jupyter` dùng CHUNG một image Docker.

### 5.3. Worker không kết nối được Master
- **Hiện tượng:** Kiểm tra `http://localhost:8080` không thấy Worker nào active.
- **Cách xử lý:** Kiểm tra firewall, đảm bảo port 7077 thông suốt. Container `spark-worker` phải phân giải được tên miền `spark-master` (Docker Network tự xử lý việc này).

---
*Tài liệu này dùng để lưu hành nội bộ và hướng dẫn triển khai.*
