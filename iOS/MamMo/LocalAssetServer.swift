import Foundation
import Network

/// Serves bundled assets on loopback only. User story data stays in WKWebView's IndexedDB.
final class LocalAssetServer {
    private let listener: NWListener
    private let queue = DispatchQueue(label: "com.mammo.reader.local-assets")
    private let root: URL
    init(port: UInt16) throws {
        guard let root = Bundle.main.url(forResource: "WebAssets", withExtension: nil) else { throw NSError(domain: "MamMo", code: 1, userInfo: [NSLocalizedDescriptionKey: "Thiếu thư mục WebAssets trong dự án Xcode."]) }
        self.root = root.standardizedFileURL
        let parameters = NWParameters.tcp
        parameters.requiredLocalEndpoint = .hostPort(host: "127.0.0.1", port: NWEndpoint.Port(rawValue: port)!)
        listener = try NWListener(using: parameters)
    }
    func start(completion: @escaping (Result<Void, Error>) -> Void) {
        var reported = false
        listener.stateUpdateHandler = { state in
            guard !reported else { return }
            switch state { case .ready: reported = true; completion(.success(())); case .failed(let error): reported = true; completion(.failure(error)); default: break }
        }
        listener.newConnectionHandler = { [weak self] connection in
            guard let self = self else { return }
            connection.start(queue: self.queue)
            self.receive(connection, accumulated: Data())
        }
        listener.start(queue: queue)
    }
    func stop() { listener.cancel() }
    private func receive(_ connection: NWConnection, accumulated: Data) {
        connection.receive(minimumIncompleteLength: 1, maximumLength: 8192) { [weak self] data, _, complete, error in
            guard let self = self else { connection.cancel(); return }
            var request = accumulated
            if let data = data { request.append(data) }
            if request.count > 16384 { connection.cancel(); return }
            if let text = String(data: request, encoding: .utf8), text.contains("\r\n\r\n") { self.respond(connection, request: text) }
            else if complete || error != nil { connection.cancel() }
            else { self.receive(connection, accumulated: request) }
        }
    }
    private func respond(_ connection: NWConnection, request: String) {
        let tokens = (request.components(separatedBy: "\r\n").first ?? "").split(separator: " ")
        guard tokens.count >= 2, tokens[0] == "GET" || tokens[0] == "HEAD" else { send(connection, status: "405 Method Not Allowed", mime: "text/plain", body: Data()); return }
        let encoded = String(tokens[1]).components(separatedBy: "?")[0]
        let path = encoded.removingPercentEncoding ?? encoded
        guard path.hasPrefix("/"), !path.components(separatedBy: "/").contains(".."), !path.contains("\0") else { send(connection, status: "403 Forbidden", mime: "text/plain", body: Data()); return }
        let relative = path == "/" ? "index.html" : String(path.dropFirst())
        let file = root.appendingPathComponent(relative).standardizedFileURL
        guard file.path.hasPrefix(root.path + "/"), let bytes = try? Data(contentsOf: file) else { send(connection, status: "404 Not Found", mime: "text/plain", body: Data()); return }
        let types = ["html":"text/html; charset=utf-8","js":"application/javascript; charset=utf-8","css":"text/css; charset=utf-8","json":"application/json","png":"image/png","webp":"image/webp","svg":"image/svg+xml","webmanifest":"application/manifest+json"]
        send(connection, status: "200 OK", mime: types[file.pathExtension] ?? "application/octet-stream", body: tokens[0] == "HEAD" ? Data() : bytes)
    }
    private func send(_ connection: NWConnection, status: String, mime: String, body: Data) {
        let header = "HTTP/1.1 \(status)\r\nContent-Type: \(mime)\r\nContent-Length: \(body.count)\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n"
        var response = Data(header.utf8); response.append(body)
        connection.send(content: response, completion: .contentProcessed { _ in connection.cancel() })
    }
}
