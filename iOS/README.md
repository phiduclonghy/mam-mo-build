# Mầm Mơ iOS — dự án Xcode, chưa có IPA

Website có cấu hình âm thanh đã xuất bản: https://mam-mo-book-1109.margaretevansa9281.chatgpt.site

## Dùng ngay trên iPhone

Mở website bằng Safari → đăng nhập tài khoản có quyền truy cập → Chia sẻ → Thêm vào Màn hình chính.

Tệp riêng `Mam-Mo-iPhone.mobileconfig` chỉ thêm biểu tượng mở website, không phải ứng dụng IPA. Hồ sơ chưa ký chỉ chứa Web Clip có thể gỡ bỏ, không chứa VPN, MDM, chứng chỉ hay tài khoản. Có thể dùng cách Safari ở trên thay cho hồ sơ.

## Chạy bằng Xcode

1. Dùng máy Mac có Xcode 15 trở lên; mở `MamMo.xcodeproj`.
2. Chọn scheme MamMo và một iPhone Simulator rồi bấm Run. Hoặc chạy `sh build_ios.sh` để build cho simulator.
3. Để chạy trên iPhone thật, vào Signing & Capabilities, chọn Team Apple của bạn và bundle identifier phù hợp.
4. Chọn thiết bị thật hoặc Any iOS Device, Product → Archive → Distribute App để tạo bản phân phối khi tài khoản/chứng chỉ/provisioning đáp ứng yêu cầu.

Không có IPA trong gói: môi trường tạo gói chạy Linux, không có Xcode hay cấu hình ký của bạn. Không có chứng chỉ hoặc thông tin Apple cá nhân được nhúng trong nguồn. Mã Swift và dự án Xcode chưa được biên dịch hoặc thử trên thiết bị.

## Nội dung và dữ liệu

- Mục tiêu iOS 15 trở lên; UIKit + WKWebView + AVFoundation + Network, không có phụ thuộc bên thứ ba.
- Thư mục `MamMo/WebAssets` có 503 truyện Anh–Việt, 2.518 trang và minh họa.
- Máy chủ loopback chỉ phục vụ tệp có sẵn tại 127.0.0.1:18763. Không lắng nghe mạng LAN và không gửi dữ liệu truyện qua máy chủ ngoài.
- Đọc ngoại tuyến, điểm chạm, hiệu ứng, tìm kiếm và tạo/sửa truyện dùng giao diện v3. Giọng đọc qua AVSpeechSynthesizer, phụ thuộc giọng đã cài trên iPhone.
- Truyện/ảnh tự thêm nằm trong IndexedDB của WKWebView, chỉ lưu trên thiết bị; không đồng bộ tự động với website. Gỡ ứng dụng có thể xóa dữ liệu này.
- Nút Website mở Safari để dùng bản trực tuyến và kho dữ liệu theo tài khoản.
- 500 truyện mới được tạo có cấu trúc từ 50 hoạt động × 10 hướng phát triển; có nội dung và bối cảnh dùng lại.

## Kiểm tra

Đã kiểm tra plist/XML, tham chiếu tệp Xcode, các tệp JavaScript và nội dung truyện. Còn cần build Xcode, kiểm thử lưu IndexedDB, ảnh, giọng đọc, xoay màn hình và thiết bị thật trước khi phát hành.

Tài liệu Apple Xcode: https://developer.apple.com/xcode/

## Cấu hình âm thanh (bản mã nguồn mới)

Mở truyện → **Âm thanh** → sửa truyện riêng hoặc tạo bản riêng của truyện có sẵn → tải giọng Việt/Anh theo trang và nhạc nền → **Lưu truyện**. Hỗ trợ MP3/M4A/WAV, 20 MB mỗi tệp. Nhạc nền chỉ phát khi bé bấm bật. Âm lượng file giọng kể và nhạc nền cấu hình riêng; phần đọc từng câu/đồ vật vẫn dùng giọng hệ thống.

File được lưu cùng truyện trong IndexedDB trên thiết bị. File dài làm truyện lớn; nên nén MP3 và chia theo trang. Nếu bản nháp vượt bộ nhớ lưu tạm, ứng dụng nhắc bấm Lưu truyện. Cấu hình này chưa được kiểm thử trên WebView/thiết bị thật và chưa phát hành APK/IPA. Website đã xuất bản bản có âm thanh.

## Bộ lệnh đóng gói mới

Trên Mac: dùng `build_ipa.py` và `signing.example.json` để xuất IPA có chữ ký. Cần import certificate/private key vào Keychain và có provisioning profile khớp ứng dụng, còn hạn, chứa UDID thiết bị. Chạy `python3 build_ipa.py --help` để xem tham số.

Bộ gói tổng hợp `Mam-Mo-Build-Kit.zip` có workflow GitHub Actions để build trên máy chủ. Workflow chưa được chạy.
