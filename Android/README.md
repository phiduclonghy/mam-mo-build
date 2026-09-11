# Mầm Mơ Android — dự án để build, chưa có APK

Website có cấu hình âm thanh đã xuất bản: https://mam-mo-book-1109.margaretevansa9281.chatgpt.site

## Dùng ngay

Mở website bằng Chrome trên Android, đăng nhập tài khoản có quyền truy cập, chọn menu ⋮ → Cài đặt ứng dụng / Thêm vào Màn hình chính.

## Tạo APK từ dự án này

Gói này là mã nguồn Android, KHÔNG phải APK. Môi trường tạo gói thiếu Android SDK; lần tải công cụ không hoàn tất do quyền mạng, nên chưa biên dịch hoặc thử trên điện thoại.

Cách nhanh khi máy đã có Android Studio:

1. Cài JDK 17, Python 3 và Android SDK Platform 35 cùng Build-tools qua SDK Manager.
2. Đặt `ANDROID_SDK_ROOT` trỏ đến thư mục SDK nếu khác vị trí mặc định.
3. Trong thư mục dự án chạy `python build_apk.py`.
4. Khi build và kiểm tra chữ ký thành công, nhận `Mam-Mo-Android-debug.apk`. Cài APK này trên thiết bị thử nghiệm theo hướng dẫn của Android.

Script dùng trực tiếp aapt2, javac, d8, zipalign và apksigner; không tải Gradle. Không có APK giả hoặc tệp đổi đuôi trong gói. APK sinh ra dùng khóa debug tại `build/manual/debug.keystore`, không dùng để phát hành thương mại.

Có thể mở thư mục bằng Android Studio với cấu hình Gradle đã cung cấp; dự án không kèm Gradle Wrapper vì chưa có công cụ để tạo/kiểm tra Wrapper ở môi trường này. Build Gradle cần Gradle 8.9 và Android Gradle Plugin 8.7.3.

## Nội dung và dữ liệu

- Android 6.0 trở lên, thư viện 503 truyện Anh–Việt nằm trong `app/src/main/assets/web`.
- Đọc ngoại tuyến, điểm chạm, hiệu ứng chiều sâu, tìm kiếm và tạo/sửa truyện dùng cùng giao diện web v3.
- Giọng đọc dùng Android TextToSpeech. Cần có giọng Việt/Anh trên máy; giọng phụ thuộc mạng có thể không đọc khi ngoại tuyến.
- Truyện tự thêm và ảnh lưu trong IndexedDB riêng của ứng dụng trên thiết bị. Không tự đồng bộ với dữ liệu D1/R2 trên website. Xóa dữ liệu ứng dụng hoặc gỡ ứng dụng có thể mất truyện tự tạo.
- Nút Website mở bản trực tuyến trong trình duyệt hệ thống để đăng nhập và dùng kho truyện theo tài khoản.
- 500 truyện mới được tạo từ 50 hoạt động × 10 hướng phát triển, có đoạn/cấu trúc dùng chung; không có 500 bộ ảnh riêng.

## Kiểm tra

Đã kiểm tra cú pháp JavaScript/Python, manifest XML, tài nguyên và số lượng 503 truyện. Chưa xác minh biên dịch Java/Android, APK, giao diện WebView hay thiết bị thật.

Tài liệu SDK chính thức: https://developer.android.com/studio

## Cấu hình âm thanh (bản mã nguồn mới)

Mở truyện → **Âm thanh** → sửa truyện riêng hoặc tạo bản riêng của truyện có sẵn → tải giọng Việt/Anh theo trang và nhạc nền → **Lưu truyện**. Hỗ trợ MP3/M4A/WAV, 20 MB mỗi tệp. Nhạc nền chỉ phát khi bé bấm bật. Âm lượng file giọng kể và nhạc nền cấu hình riêng; phần đọc từng câu/đồ vật vẫn dùng giọng hệ thống.

File được lưu cùng truyện trong IndexedDB trên thiết bị. File dài làm truyện lớn; nên nén MP3 và chia theo trang. Nếu bản nháp vượt bộ nhớ lưu tạm, ứng dụng nhắc bấm Lưu truyện. Cấu hình này chưa được kiểm thử trên WebView/thiết bị thật và chưa phát hành APK/IPA. Website đã xuất bản bản có âm thanh.

## Bộ lệnh đóng gói mới

Windows: chạy `DONG-GOI-ANDROID.cmd` sau khi cài Android Studio (SDK 35/Build-tools 35.0.1) và Python. Script tự tìm JBR của Android Studio; APK chỉ được báo thành công sau khi kiểm tra chữ ký.

Bộ gói tổng hợp `Mam-Mo-Build-Kit.zip` có workflow GitHub Actions để build trên máy chủ. Workflow chưa được chạy.
