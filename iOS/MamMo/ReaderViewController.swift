import UIKit
import WebKit
import AVFoundation

final class ReaderViewController: UIViewController, WKNavigationDelegate, WKScriptMessageHandler, AVSpeechSynthesizerDelegate {
    private var web: WKWebView!
    private var server: LocalAssetServer?
    private let speaker = AVSpeechSynthesizer()
    private var identifiers: [ObjectIdentifier: String] = [:]
    private let online = URL(string: "https://mam-mo-book-1109.margaretevansa9281.chatgpt.site")!
    private let localURL = URL(string: "http://127.0.0.1:18763/")!

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Mầm Mơ · Đọc trên máy"
        view.backgroundColor = UIColor(red: 0.98, green: 0.97, blue: 0.95, alpha: 1)
        navigationItem.rightBarButtonItem = UIBarButtonItem(title: "Website ↗", style: .plain, target: self, action: #selector(openWebsite))
        navigationController?.navigationBar.tintColor = UIColor(red: 0.09, green: 0.25, blue: 0.22, alpha: 1)
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        config.userContentController.add(self, name: "mammo")
        let voices = AVSpeechSynthesisVoice.speechVoices().filter { $0.language.hasPrefix("vi") || $0.language.hasPrefix("en") }.map { ["name": $0.name, "lang": $0.language] }
        let voiceJSON = String(data: try! JSONSerialization.data(withJSONObject: voices), encoding: .utf8)!
        let script = """
        window.MamMoNative={
          voices:function(){return JSON.stringify(\(voiceJSON));},
          speak:function(id,text,lang,rate){window.webkit.messageHandlers.mammo.postMessage({action:'speak',id:id,text:text,lang:lang,rate:rate});},
          stop:function(){window.webkit.messageHandlers.mammo.postMessage({action:'stop'});}
        };
        """
        config.userContentController.addUserScript(WKUserScript(source: script, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = self
        web.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(web)
        NSLayoutConstraint.activate([web.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor), web.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor), web.leadingAnchor.constraint(equalTo: view.leadingAnchor), web.trailingAnchor.constraint(equalTo: view.trailingAnchor)])
        speaker.delegate = self
        NotificationCenter.default.addObserver(self, selector: #selector(pauseSpeech), name: UIApplication.willResignActiveNotification, object: nil)
        do {
            let server = try LocalAssetServer(port: 18763)
            self.server = server
            server.start { [weak self] result in
                DispatchQueue.main.async {
                    guard let self = self else { return }
                    switch result {
                    case .success: self.web.load(URLRequest(url: self.localURL))
                    case .failure(let error): self.showError(error.localizedDescription)
                    }
                }
            }
        } catch { showError(error.localizedDescription) }
    }
    @objc private func openWebsite() { UIApplication.shared.open(online) }
    @objc private func pauseSpeech() { speaker.stopSpeaking(at: .immediate); web?.evaluateJavaScript("window.dispatchEvent(new Event(\"mammo-pause\"))", completionHandler: nil) }
    private func showError(_ text: String) {
        let alert = UIAlertController(title: "Chưa mở được thư viện trên máy", message: text, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Mở website", style: .default) { [weak self] _ in self?.openWebsite() })
        alert.addAction(UIAlertAction(title: "Đóng", style: .cancel))
        present(alert, animated: true)
    }
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        if url.host == "127.0.0.1" && url.port == 18763 { decisionHandler(.allow) }
        else { if navigationAction.targetFrame?.isMainFrame != false && url.scheme == "https" { UIApplication.shared.open(url) }; decisionHandler(.cancel) }
    }
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.frameInfo.isMainFrame, message.frameInfo.securityOrigin.host == "127.0.0.1", let data = message.body as? [String: Any], let action = data["action"] as? String else { return }
        if action == "stop" { speaker.stopSpeaking(at: .immediate); return }
        guard action == "speak", let id = data["id"] as? String, let text = data["text"] as? String, let language = data["lang"] as? String else { return }
        speaker.stopSpeaking(at: .immediate)
        guard let voice = AVSpeechSynthesisVoice(language: language) else { speechEvent(id, "error"); return }
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = voice
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate * Float(max(0.5, min(1.6, (data["rate"] as? Double) ?? 1)))
        identifiers[ObjectIdentifier(utterance)] = id
        speaker.speak(utterance)
    }
    private func speechEvent(_ id: String, _ type: String) {
        guard let bytes = try? JSONSerialization.data(withJSONObject: [id, type]), let arguments = String(data: bytes, encoding: .utf8) else { return }
        web.evaluateJavaScript("window.__mammoSpeechEvent && window.__mammoSpeechEvent.apply(null,\(arguments))", completionHandler: nil)
    }
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didStart utterance: AVSpeechUtterance) { if let id = identifiers[ObjectIdentifier(utterance)] { speechEvent(id, "start") } }
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) { if let id = identifiers.removeValue(forKey: ObjectIdentifier(utterance)) { speechEvent(id, "end") } }
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) { identifiers.removeValue(forKey: ObjectIdentifier(utterance)) }
    deinit { NotificationCenter.default.removeObserver(self); server?.stop(); speaker.stopSpeaking(at: .immediate) }
}
