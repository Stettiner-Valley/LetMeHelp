import os
import webview

class Api:
    def test(self):
        print('It works!')


if __name__ == '__main__':
    api = Api()
    webview.create_window('LetMeHelp User Client', 'assets/index.html', js_api=api, min_size=(600, 450))
    # TODO: Fails with cert = QSslCertificate.fromPath(certfile)[0] inidex out of range when ssl=True
    webview.start(ssl=False)