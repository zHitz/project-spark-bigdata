# BÁO CÁO KỸ THUẬT: PHÂN TÍCH & XỬ LÝ DỮ LIỆU JSON PHỨC TẠP VỚI APACHE SPARK

**Đề tài:** Xử lý dữ liệu lồng nhau (Nested Data) từ GitHub Archive.
**Tài liệu này trình bày chi tiết về Logic, Nguyên lý hoạt động và Lý do lựa chọn giải pháp.**

---

## I. TẠI SAO PHẢI SỬ DỤNG APACHE SPARK CHO BÀI TOÁN NÀY?

### 1. Bối cảnh & Thách thức của dữ liệu
Dữ liệu từ GitHub Archive (và nhiều nguồn Big Data khác như Logs, IoT, Mobile Events) thường được lưu dưới dạng **JSON bán cấu trúc (Semi-structured)**. Điểm đặc trưng của loại dữ liệu này là:
*   **Cấu trúc lồng nhau (Nested)**: Một đối tượng chứa đối tượng khác (Ví dụ: `commit` nằm trong `payload`, `author` nằm trong `commit`).
*   **Chứa mảng (Arrays)**: Một sự kiện có thể chứa danh sách nhiều hành động con (Ví dụ: 1 lần `PushEvent` chứa danh sách 10 `commits`).
*   **Schema động**: Cấu trúc có thể thay đổi theo thời gian hoặc thiếu field ở một số bản ghi.

Nếu sử dụng các hệ quản trị cơ sở dữ liệu quan hệ truyền thống (RDBMS) như MySQL hay SQL Server, ta sẽ gặp các vấn đề:
1.  **Cứng nhắc**: Phải định nghĩa bảng (Table Schema) trước khi nạp dữ liệu.
2.  **Khó xử lý mảng**: Phải tạo bảng phụ (Join tables) để lưu trữ quan hệ 1-n, làm tăng độ phức tạp khi ETL.
3.  **Hiệu năng thấp**: Rất chậm khi quét (scan) lượng dữ liệu lớn (Terabytes) để tìm kiếm thông tin sâu bên trong JSON.

### 2. Lý do chọn Apache Spark
Apache Spark giải quyết triệt để các vấn đề trên nhờ các đặc tính:
*   **Schema-on-Read**: Spark tự động suy luận cấu trúc dữ liệu khi đọc file (Inference), không cần định nghĩa bảng trước.
*   **Hỗ trợ kiểu dữ liệu phức tạp**: Spark SQL hỗ trợ native các kiểu dữ liệu `StructType` (đối tượng lồng nhau) và `ArrayType` (mảng), cho phép truy vấn trực tiếp bằng SQL (`col.field`) mà không cần tách bảng.
*   **Xử lý phân tán (Distributed Computing)**: Dữ liệu được chia nhỏ (Partition) và xử lý song song trên nhiều node (Worker), giúp tốc độ nhanh hơn hàng trăm lần so với xử lý đơn luồng.
*   **In-Memory Processing**: Xử lý dữ liệu trên RAM giúp giảm thiểu I/O ổ cứng.

---

## II. NGUYÊN LÝ HOẠT ĐỘNG VÀ LOGIC XỬ LÝ (THE CORE LOGIC)

Quy trình xử lý của đồ án dựa trên kỹ thuật **"Flattening" (Làm phẳng)**. Dưới đây là phân tích chi tiết từng bước logic diễn ra bên trong hệ thống.

### Bước 1: Ingestion (Nạp dữ liệu & Suy luận Schema)
Khi lệnh `spark.read.json("path/to/file")` được thực thi:
1.  Spark quét một phần (hoặc toàn bộ) file để xác định kiểu dữ liệu.
2.  Nó nhận diện rằng trường `payload` không phải là String, mà là một `StructType` chứa các trường con.
3.  Nó nhận diện `payload.commits` là một `ArrayType(StructType)`, tức là một danh sách các đối tượng.

*Tại bước này, dữ liệu vẫn ở dạng nguyên thủy, chưa bị biến đổi, giữ nguyên tính chất lồng nhau.*

### Bước 2: Kỹ thuật "Explode" (Bùng nổ dữ liệu) - MẤU CHỐT CỦA ĐỀ TÀI
Đây là bước quan trọng nhất để chuyển đổi từ dạng "Document" sang dạng "Relation" (Bảng).

Giả sử ta có 1 bản ghi sự kiện (Row) như sau:
```json
{ "id": 1, "commits": [ {"sha": "A"}, {"sha": "B"} ] }
```
Đây là 1 dòng dữ liệu, nhưng chứa thông tin của 2 commit. Nếu muốn phân tích từng commit, ta phải tách nó ra.

Hàm `explode(col("commits"))` hoạt động theo nguyên lý tích Đề-các (Cartesian product) cục bộ:
*   Nó nhân bản các cột bên ngoài (`id`) tương ứng với số lượng phần tử trong mảng bên trong.
*   Kết quả logic sẽ biến đổi 1 dòng thành 2 dòng:
    1. `id: 1, commit: {"sha": "A"}`
    2. `id: 1, commit: {"sha": "B"}`

**Tại sao dùng Explode?**
Nếu không dùng Explode, ta không thể group by, count, hay filter trên từng commit riêng lẻ được. Explode giúp "bình đẳng hóa" các phần tử trong mảng thành các dòng độc lập.

### Bước 3: Truy xuất thuộc tính lồng nhau (Dot Notation Traversal)
Sau khi explode, cột `commit` bây giờ là một `Struct` (một object đơn). Để đưa về dạng bảng phẳng (CSV/Excel), ta cần "kéo" các giá trị con ra ngoài.

Spark cho phép dùng dấu chấm (.) để đi xuyên qua cấu trúc:
*   `col("commit.author.email")`: Đi từ cột `commit` -> vào struct `author` -> lấy giá trị `email`.
*   Logic này giúp ta trích xuất chính xác thông tin ở độ sâu bất kỳ (Level N) và đặt lại tên (Alias) thành một cột ở Level 1.

### Bước 4: Transformation & Action (DAG Execution)
Trong Spark, các lệnh như `select`, `explode`, `filter` là **Lazy Evaluation** (Đánh giá lười).
*   Khi bạn chạy code python, Spark chưa thực sự xử lý dữ liệu ngay. Nó chỉ xây dựng một "Kế hoạch thực thi" (Directed Acyclic Graph - DAG).
*   Chỉ khi gọi lệnh **Action** (như `count()`, `show()`, `write`), Spark mới thực sự:
    1.  Đọc file từ đĩa.
    2.  Thực hiện filter ngay khi đọc (Predicate Pushdown) để giảm dữ liệu thừa.
    3.  Thực hiện Explode và Project (Select) trên RAM.
    4.  Ghi kết quả xuống đĩa.

---

## III. KIẾN TRÚC TRIỂN KHAI HỆ THỐNG (SYSTEM ARCHITECTURE)

Hệ thống được triển khai trên nền tảng **Docker Container** để mô phỏng một môi trường Production thực tế.

### 1. Tại sao dùng Docker?
*   **Cô lập môi trường**: Tránh việc cài đặt Java/Scala/Python trên máy chủ làm xung đột với các phần mềm khác.
*   **Đồng nhất (Consistency)**: Đảm bảo rằng phiên bản Python trên Driver (nơi chạy Code Jupyter) và Executor (nơi xử lý dữ liệu ngầm) là **hoàn toàn giống nhau** (Python 3.11). Đây là yếu tố sống còn để tránh lỗi "Python Worker failed to connect back".

### 2. Các thành phần trong cụm (Cluster Components)

#### A. Spark Master (Cluster Manager)
*   Đóng vai trò "Bộ não" của hệ thống.
*   Nhiệm vụ: Quản lý tài nguyên (CPU/RAM) của các Worker. Khi nhận được lệnh từ Jupyter, Master sẽ quyết định Worker nào sẽ thực hiện nhiệm vụ gì.

#### B. Spark Worker (Executor)
*   Đóng vai trò "Cơ bắp".
*   Nhiệm vụ: Thực tế chạy các logic `explode`, `filter`...
*   Trong dự án này, Worker được cấp phát 1GB RAM. Dữ liệu JSON được load vào RAM của Worker để xử lý.

#### C. Jupyter Notebook (Driver Program)
*   Đóng vai trò "Giao diện điều khiển".
*   Nơi lập trình viên viết code PySpark.
*   Khi chạy code, Jupyter gửi một `SparkContext` tới Master để yêu cầu tính toán.

---

## IV. TỔNG KẾT

Giải pháp này kết hợp sức mạnh của:
1.  **Spark SQL**: Để xử lý logic phức tạp của JSON lồng nhau một cách tường minh và hiệu quả.
2.  **Cấu trúc Flattening**: Để biến đổi dữ liệu phi cấu trúc thành có cấu trúc, phục vụ báo cáo.
3.  **Docker Microservices**: Để chuẩn hóa việc triển khai và vận hành.

Đây là mô hình tiêu chuẩn hiện nay trong các công ty công nghệ (Data Lakehouse Architecture) để xử lý dữ liệu log hành vi người dùng.

## V. TỐI ƯU HÓA VỚI CATALYST OPTIMIZER (LÝ THUYẾT NÂNG CAO)

Trong hình ảnh bạn cung cấp, đó là kiến trúc của **Spark Catalyst Optimizer**. Đây là "trái tim" của Spark SQL.

### 1. Nó hoạt động thế nào trong dự án này?
Khi bạn viết lệnh: `df.select(...).explode(...)`
1.  **Unresolved Logical Plan**: Spark nhận lệnh nhưng chưa biết cột nào đúng sai.
2.  **Logical Plan**: Spark kiểm tra các tên cột trong Schema (đảm bảo `payload.commits` có tồn tại).
3.  **Optimized Logical Plan**: Catalyst sẽ tối ưu hóa. Ví dụ: Bạn `filter` (lọc PushEvent) và `explode` (tách mảng). Catalyst thông minh sẽ đẩy việc `filter` lên trước (Filter Pushdown) để giảm số lượng dòng cần `explode`, giúp chạy nhanh hơn gấp nhiều lần.
4.  **Physical Plan**: Chọn cách chạy thực tế (Join kiểu gì, Shuffle ra sao) và sinh ra Java Bytecode để chạy trên các Worker.

### 2. Ý nghĩa
Nhờ cơ chế này, bạn viết code Python (dễ viết) nhưng Spark sẽ tự động dịch sang Java Bytecode tối ưu (chạy cực nhanh). Bạn không cần phải code thủ công phần tối ưu này.

