# Mầm Mơ — bộ đóng gói Android/iOS và website

Website đã xuất bản bản có âm thanh ngày 11/09/2026:
https://mam-mo-book-1109.margaretevansa9281.chatgpt.site

**Đây là bộ mã nguồn + lệnh build, chưa chứa APK hoặc IPA đã biên dịch.** Không có Android SDK/JDK compiler trong môi trường tạo gói; lượt tải SDK bị chặn ở bước xin quyền mạng. iOS cần macOS/Xcode và chữ ký của bạn. Không có tài khoản GitHub/Apple hay chứng chỉ ký nào được gắn vào gói.

## Dùng ngay trên điện thoại

- iPhone: mở link bằng Safari → đăng nhập tài khoản có quyền → Chia sẻ → Thêm vào Màn hình chính. Nếu có tùy chọn “Mở dưới dạng ứng dụng web”, bật lên.
- Android: mở bằng Chrome → đăng nhập → menu ⋮ → Cài đặt ứng dụng / Thêm vào Màn hình chính.
- Đây là bản web cài lên màn hình chính (PWA). Bản native bên dưới đọc 503 truyện từ tài nguyên trong ứng dụng và lưu truyện tự thêm trên máy; dữ liệu này không tự đồng bộ với website.
- Website hiện riêng tư cho tài khoản chủ sở hữu. Gửi link không tự cấp quyền cho người khác. Không cần thuê hosting khác để dùng địa chỉ này.

## Cách 1 — tạo APK trên Windows

1. Cài Android Studio và Python 3. Android Studio: https://developer.android.com/studio
2. Android Studio → SDK Manager → cài Android SDK Platform 35 và Build-tools 35.0.1. Script dùng JDK đã có trong PATH/JAVA_HOME hoặc JBR đi kèm Android Studio.
3. Giải nén, vào `Android`, bấm đúp `DONG-GOI-ANDROID.cmd`.
4. Chỉ khi báo thành công mới có `Mam-Mo-Android-debug.apk` và tệp SHA-256. Script kiểm tra chữ ký APK, căn chỉnh và các tệp nội dung bắt buộc.
5. Chuyển APK sang Android; mở tệp và cho phép ứng dụng quản lý tệp cài ứng dụng này khi hệ điều hành hỏi. Đây là APK thử nghiệm ký debug, chưa phải bản phát hành Google Play.

Khóa debug được giữ trong `Android/build/manual/debug.keystore` để các lần build trên cùng máy có thể cập nhật ứng dụng. Khi đổi khóa, Android có thể yêu cầu gỡ bản cũ; sao lưu truyện tự thêm trước vì gỡ app làm mất dữ liệu. Gói nguồn không chứa khóa.

## Cách 2 — build bằng GitHub Actions

Workflow được viết sẵn, **chưa chạy trên GitHub trong lần đóng gói này**.

1. Tạo một repository GitHub của bạn và đưa **nội dung** bộ gói vào thư mục gốc. Thư mục `Android`, `iOS`, `ci` và workflow `build-apps.yml` phải ở đúng cấu trúc trong gói. Giữ repository riêng tư nếu bạn không muốn công khai mã nguồn.
2. GitHub → Actions → **Dong goi Mam Mo Android va iOS** → **Run workflow**.
3. Chọn `android` để chỉ lấy APK, hoặc `both` để thêm bản chạy iPhone Simulator trên Mac. Bản simulator không cài được lên iPhone thật.
4. Khi job thành công, mở phần Artifacts và tải gói tương ứng; giải nén để lấy APK/IPA. Mỗi artifact giữ 14 ngày theo cấu hình workflow.
5. Để có IPA cho iPhone thật, làm phần cấu hình chữ ký bên dưới rồi bật `signed_iphone`. Workflow chỉ xuất file, không tự đăng App Store/Google Play.

Workflow dùng máy Ubuntu và macOS do GitHub cấp; quota và phí chạy theo tài khoản GitHub của bạn. Không bắt đầu job nào trong lần tạo gói này. Cơ sở cấu hình: [GitHub runner Ubuntu](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md), [macOS runner](https://github.com/actions/runner-images/blob/main/images/macos/macos-15-Readme.md).

## Chữ ký iOS để tạo IPA cài trên iPhone

Apple yêu cầu bản ứng dụng được build và ký đúng để cài trên thiết bị. Hướng dẫn chính thức: [Distributing your app to registered devices](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices).

Trong Apple Developer, cần có:

- Apple Team ID và App ID/bundle ID (mặc định mã nguồn là `com.mammo.reader`, có thể đổi).
- Apple Distribution certificate với private key, xuất thành `.p12` có mật khẩu.
- Ad Hoc provisioning profile đúng bundle ID, đúng certificate và chứa UDID của từng iPhone sẽ cài ứng dụng.

Đối với GitHub, đặt năm giá trị tại Settings → Secrets and variables → Actions:

| Secret | Nội dung |
| --- | --- |
| `IOS_CERTIFICATE_P12_BASE64` | Base64 một dòng của tệp chứng chỉ `.p12` |
| `IOS_CERTIFICATE_PASSWORD` | Mật khẩu `.p12` |
| `IOS_PROFILE_BASE64` | Base64 một dòng của Ad Hoc `.mobileprovision` |
| `IOS_TEAM_ID` | Team ID 10 ký tự |
| `IOS_BUNDLE_ID` | Bundle ID khớp provisioning profile |

Không gửi mật khẩu Apple ID hoặc private key qua chat, không commit các giá trị trên vào repository. Workflow nhập chữ ký vào Keychain tạm, kiểm tra profile còn hạn/đúng app/có thiết bị và xóa dữ liệu ký sau job. Tham khảo [GitHub: ký ứng dụng Xcode trên runner](https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/sign-xcode-applications).

IPA Ad Hoc sau khi tạo chỉ cài được trên thiết bị có UDID trong profile. Dùng Xcode/Apple Configurator hoặc phương thức phân phối Ad Hoc hợp lệ; mở một tệp IPA trong ứng dụng Files không tự cài app. Để phân phối bằng TestFlight/App Store, cần quy trình App Store Connect riêng.

## Tạo IPA trên Mac của bạn

1. Cài Xcode, mở lần đầu để hoàn tất cài công cụ. Import `.p12` của bạn vào Keychain.
2. Vào `iOS`, chép `signing.example.json` thành `signing.json`; điền Team ID/bundle ID. Dùng `release-testing` cho Ad Hoc, `debugging` cho profile Development, hoặc `app-store-connect` khi chuẩn bị đưa lên TestFlight/App Store.
3. Đặt profile hợp lệ ở `iOS/profile.mobileprovision` rồi chạy `python3 build_ipa.py` hoặc `sh DONG-GOI-IPHONE.command`.
4. Chỉ khi Xcode archive/export và kiểm tra thành công mới nhận `Mam-Mo-iPhone.ipa` cùng SHA-256.

Chưa có tài khoản Developer: có thể mở `MamMo.xcodeproj` trên Mac, chọn Signing Team rồi Run lên iPhone nếu tài khoản/thiết bị được Xcode cho phép. Đây không phải luồng xuất IPA phân phối của bộ script này.

## Nội dung trong app

503 truyện Anh–Việt, 2.518 trang, hiệu ứng chiều sâu, nhân vật hoạt hình, điểm chạm, thêm/sửa truyện, file giọng kể hai ngôn ngữ theo trang và nhạc nền. Truyện tự thêm lưu trong IndexedDB riêng từng app; website lưu theo tài khoản. Âm thanh MP3/M4A/WAV tối đa 20 MB/file; trang chưa có file dùng giọng hệ thống. 500 truyện mới được tạo có cấu trúc, có đoạn và bối cảnh dùng chung.

## Trạng thái kiểm tra

- Website: đã triển khai thành công bản có âm thanh; 16 kiểm tra tự động của website đã qua ở lượt trước.
- Bộ đóng gói: đã kiểm tra cú pháp Python/JavaScript/shell, XML/plist, cấu trúc workflow và kiểm tra điều kiện cấu hình ký iOS.
- Chưa biên dịch native, chưa chạy GitHub Actions, chưa tạo APK/IPA, chưa kiểm thử trên điện thoại thật. Các giới hạn này phải được xử lý trước khi phát hành ứng dụng.
