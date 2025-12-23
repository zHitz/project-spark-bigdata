# Outline Báo Cáo PowerPoint (Slide)

## Slide 1: Trang bìa
- Tên đề tài: **Phân tích dữ liệu JSON lồng nhau phức tạp với Apache Spark**
- Đề tài số: 25
- GVHD: ...
- Nhóm thực hiện: ...

## Slide 2: Giới thiệu bài toán
- **Bối cảnh**: Dữ liệu Big Data thường ở dạng JSON lồng nhau (Logs, NoSQL).
- **Thách thức**: Khó phân tích bằng SQL thường, cấu trúc phức tạp (Array of Structs).
- **Mục tiêu**: Xây dựng pipeline "Flattener" dùng Spark SQL.

## Slide 3: Dữ liệu GitHub Archive
- Nguồn: GH Archive.
- Định dạng: NDJSON, nén Gzip.
- Cấu trúc: Lồng nhau 5-6 cấp.
- Minh họa: Ảnh chụp mẫu JSON (Raw).

## Slide 4: Giải pháp công nghệ
- **Apache Spark**: Xử lý phân tán, In-memory.
- **Spark SQL Functions**:
    - `explode()`: Tách mảng thành dòng.
    - `col("a.b.c")`: Truy xuất lồng nhau.
- **Docker**: Môi trường triển khai đồng nhất.

## Slide 5: Kiến trúc hệ thống
- (Chèn hình sơ đồ từ báo cáo)
- Raw JSON -> Spark Cluster -> Processed CSV -> Dashboard.

## Slide 6: Demo thực nghiệm
- Input: Dữ liệu log GitHub (~2015).
- Quá trình: ETL bằng PySpark (Jupyter Notebook).
- Output: Bảng dữ liệu phẳng (Relational Table).

## Slide 7: Dashboard kết quả
- Biểu đồ 1: Top 10 Contributors.
- Biểu đồ 2: Top 10 Active Repositories.
- (Chèn ảnh chụp màn hình notebook/Excel chart).

## Slide 8: Kết luận
- **Kết quả**: Xử lý thành công dữ liệu phức tạp, hiệu năng cao.
- **Bài học**: Kỹ năng xử lý Dataframe, tối ưu hóa Spark job.
- **Hướng phát triển**: Real-time Streaming.

## Slide 9: Q&A
- Cảm ơn và hỏi đáp.
