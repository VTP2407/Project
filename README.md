# Diabetes Multi-Agent AI Support System

Hệ thống Hỗ Trợ Đái Tháo Đường Đa Tác Nhân (Multi-Agent System) tích hợp Trí tuệ Nhân tạo toàn diện: Machine Learning (XGBoost), Deep Learning (PyTorch MLP), Cơ sở Tri thức Y khoa Chuẩn & RAG (WHO/ADA/CDC), Bộ Quy Tắc Lâm Sàng Độc Lập (Rule Engine), và Mô Phỏng Học Tăng Cường (Reinforcement Learning - Q-Learning).

---

## 1. Bảo Toàn Tập Dữ Liệu Gốc (Dataset Preservation)
- **Tập tin dữ liệu gốc**: `diabetes_prediction_dataset.csv`
- **Mã băm toàn vẹn SHA-256**: `F233FC470E904201F35310D061CB46CA0A6BC7CA5C3E428B769FB4F87F69929B`
- **Quy mô**: 100,000 hồ sơ bệnh nhân thực nghiệm, 8 đặc trưng dự báo và 1 biến mục tiêu `diabetes` (0: Âm tính 91.5%, 1: Dương tính 8.5%).
- **Bảo toàn**: Tập dữ liệu gốc được lưu trữ nguyên vẹn tại `ml-training/datasets/raw/diabetes_prediction_dataset.csv`. Quy trình tiền xử lý được khớp (fitted) độc quyền trên tập Training để ngăn chặn triệt để hiện tượng rò rỉ dữ liệu (data leakage).

---

## 2. Kiến Trúc Đa Tác Nhân (Multi-Agent System)
Hệ thống sử dụng cơ chế điều phối trung tâm với 8 tác nhân chuyên trách độc lập:
1. **Orchestrator Agent**: Tiếp nhận truy vấn, phân loại ý định lâm sàng, tạo kế hoạch phân luồng điều kiện, đo lường độ trễ và tổng hợp phản hồi.
2. **Patient Context Agent**: Truy xuất hồ sơ cá nhân, BMI, tiền sử bệnh và lịch sử các lần đo đường huyết gần nhất của bệnh nhân.
3. **Health Assessment Agent**: Tiền xử lý chỉ số sinh học và kích hoạt mô hình học máy đã huấn luyện (XGBoost / PyTorch MLP) kèm độ quan trọng đặc trưng SHAP.
4. **Knowledge Agent (RAG)**: Tìm kiếm tương đồng vector trên tài liệu y khoa từ WHO, ADA, CDC và trả về trích dẫn bằng chứng cụ thể.
5. **Lifestyle Advisor Agent**: Tư vấn giáo dục dinh dưỡng cân bằng và kế hoạch vận động cá nhân hóa (tuyệt đối không kê đơn thuốc).
6. **Monitoring Agent**: Theo dõi các mốc đường huyết bất thường (hạ đường huyết &lt;70 mg/dL, tăng đường huyết &gt;=250 mg/dL).
7. **Safety Agent**: Có quyền ưu tiên cao nhất; thẩm định an toàn mọi phản hồi, ngăn chặn điều chỉnh liều lượng thuốc và đính kèm miễn trừ trách nhiệm y tế bắt buộc.
8. **Report Agent**: Tổng hợp số liệu thống kê chuỗi thời gian và xuất báo cáo lâm sàng định kỳ.

---

## 3. Danh Sách 5 Jupyter Notebook Thực Thi (ml-training/notebooks/)
Cả 5 notebook đều là tệp tin `.ipynb` thực tế, đã chạy thành công 100% trên tập dữ liệu và lưu đầy đủ đồ thị, bảng biểu:
- **`01_data_exploration.ipynb`**: Phân tích khám phá dữ liệu, phân bố nhãn mất cân bằng (10.76:1), ma trận tương quan và ngưỡng sinh học ADA.
- **`02_data_preprocessing.ipynb`**: Phân chia phân tầng Train (70%) / Val (10%) / Test (20%), mã hóa LabelEncoder và chuẩn hóa StandardScaler không rò rỉ dữ liệu.
- **`03_machine_learning_training.ipynb`**: Huấn luyện và đánh giá đối kháng Logistic Regression, Random Forest và XGBoost.
- **`04_deep_learning_training.ipynb`**: Xây dựng mạng nơ-ron sâu PyTorch MLP với hàm mất mát `BCEWithLogitsLoss(pos_weight=10.76)` giải quyết mất cân bằng lớp.
- **`05_model_evaluation.ipynb`**: So sánh toàn diện Accuracy, Precision, Recall, F1, ROC-AUC trên tập Test độc lập (20,000 mẫu) và giải thích SHAP toàn cục.

---

## 4. Tài Khoản Thử Nghiệm Sẵn Có (Seed Accounts)
Hệ thống đã nạp sẵn dữ liệu khởi tạo trong cơ sở dữ liệu:
- **Bệnh nhân (Patient Demo)**:
  - Email: `patient@diabetes.ai`
  - Mật khẩu: `Patient@123456`
  - Đã có sẵn hồ sơ sức khỏe và 10 bản ghi nhật ký đường huyết chuỗi thời gian.
- **Quản trị viên (Admin)**:
  - Email: `admin@diabetes.ai`
  - Mật khẩu: `Admin@123456`
  - Có toàn quyền truy cập: Giám sát Multi-Agent, Quản lý Quy tắc Lâm sàng, Quản lý Tri thức RAG, Đánh giá Mô hình ML/DL và Học tăng cường RL.

---

## 5. Hướng Dẫn Cài Đặt & Khởi Chạy Nhanh

### 5.1 Chạy Kiểm Thử Tự Động Backend
```bash
python Project/backend/test_backend.py
```

### 5.2 Khởi Chạy Backend (FastAPI)
```bash
cd Project/backend
python main.py
```
API phục vụ tại `http://localhost:8000` (Swagger UI: `http://localhost:8000/docs`).

### 5.3 Khởi Chạy Frontend (React + Vite + Tailwind CSS)
```bash
cd Project/frontend
npm run dev
```
Giao diện người dùng truy cập tại `http://localhost:5173`.

### 5.4 Khởi Chạy Bằng Docker Compose (Tùy chọn)
```bash
cd Project
docker-compose up --build
```
