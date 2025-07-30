from flask import Flask, render_template_string, send_from_directory
import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Navin - Local Development Server</title>
    <link rel=\"stylesheet\" href=\"/static/style.css\">
</head>
<body>
    <header class=\"header\">
        <div class=\"container\">
            <div class=\"header-content\">
                <div class=\"logo\">
                    <div class=\"logo-icon\">N</div>
                    <span class=\"logo-text\">Navin</span>
                </div>
                <nav class=\"nav\">
                    <a href=\"#status\" class=\"nav-link\">Server Status</a>
                    <a href=\"#agents\" class=\"nav-link\">Active Agents</a>
                    <a href=\"#monitoring\" class=\"nav-link\">Monitoring</a>
                    <a href=\"#docs\" class=\"nav-link\">Documentation</a>
                </nav>
                <div class=\"status-indicator\">
                    <span class=\"status-dot\"></span>
                    <span class=\"status-text\">Server Running</span>
                </div>
            </div>
        </div>
    </header>
    <main class=\"main\">
        <section class=\"hero\">
            <div class=\"container\">
                <div class=\"hero-content\">
                    <div class=\"status-badge\">
                        <span class=\"pulse-dot\"></span>
                        <span>Development Server Active</span>
                    </div>
                    <h1 class=\"hero-title\">
                        <span class=\"title-line\">Navin Framework</span>
                        <span class=\"title-line gradient-text\">Running Locally</span>
                    </h1>
                    <p class=\"hero-description\">
                        Your AI agent incentive ecosystem is now running. Monitor agent performance, 
                        track token economics, and manage your decentralized agent network.
                    </p>
                    <div class=\"quick-actions\">
                        <button class=\"btn btn-primary\">View Dashboard</button>
                        <button class=\"btn btn-glass\">Agent Console</button>
                        <button class=\"btn btn-ghost\">API Explorer</button>
                    </div>
                </div>
            </div>
        </section>
        <section class=\"dashboard\">
            <div class=\"container\">
                <div class=\"dashboard-grid\">
                    <div class=\"card\">
                        <h3 class=\"card-title\">Server Status</h3>
                        <div class=\"stats\">
                            <div class=\"stat\">
                                <div class=\"stat-value\">127.0.0.1:2401</div>
                                <div class=\"stat-label\">Server Address</div>
                            </div>
                            <div class=\"stat\">
                                <div class=\"stat-value\">Running</div>
                                <div class=\"stat-label\">Status</div>
                            </div>
                        </div>
                    </div>
                    <div class=\"card\">
                        <h3 class=\"card-title\">Active Agents</h3>
                        <div class=\"agent-list\">
                            <div class=\"agent-item\">
                                <div class=\"agent-icon\">🤖</div>
                                <div class=\"agent-info\">
                                    <div class=\"agent-name\">Agent Alpha</div>
                                    <div class=\"agent-status\">Active</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class=\"card\">
                        <h3 class=\"card-title\">Token Economics</h3>
                        <div class=\"token-stats\">
                            <div class=\"token-metric\">
                                <span class=\"token-value\">1,250</span>
                                <span class=\"token-label\">Total Tokens</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        <section class=\"contact-section\">
            <div class=\"container\">
                <div class=\"contact-card\">
                    <h2 class=\"contact-title\">Contact & Contribute</h2>
                    <p class=\"contact-description\">
                        This project explores how AI agents can be aligned with their assigned goals through economic incentives. This innovative approach aims to enhance the reliability, predictability, and security of agentic systems.<br><br>
                        As this is an emerging area of research, contributions and collaboration are highly encouraged! If you are interested in expanding the boundaries of knowledge in this field, please reach out and get in touch.
                    </p>
                    <div class=\"contact-buttons\">
                        <a href=\"https://github.com/kiranmusze/navin\" class=\"btn btn-github\" target=\"_blank\" rel=\"noopener\">
                            <svg class=\"icon\" viewBox=\"0 0 24 24\" width=\"20\" height=\"20\"><path fill=\"currentColor\" d=\"M12 2C6.48 2 2 6.58 2 12.26c0 4.5 2.87 8.32 6.84 9.67.5.09.68-.22.68-.48 0-.24-.01-.87-.01-1.7-2.78.62-3.37-1.36-3.37-1.36-.45-1.18-1.1-1.5-1.1-1.5-.9-.63.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.7 0 0 .84-.28 2.75 1.05A9.38 9.38 0 0 1 12 6.84c.85.004 1.71.12 2.51.35 1.91-1.33 2.75-1.05 2.75-1.05.55 1.4.2 2.44.1 2.7.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.81-4.57 5.07.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.58.69.48A10.01 10.01 0 0 0 22 12.26C22 6.58 17.52 2 12 2Z\"></path></svg>
                            GitHub
                        </a>
                        <a href=\"https://www.linkedin.com/in/kiran-banakar/\" class=\"btn btn-linkedin\" target=\"_blank\" rel=\"noopener\">
                            <svg class=\"icon\" viewBox=\"0 0 24 24\" width=\"20\" height=\"20\"><path fill=\"currentColor\" d=\"M19 0h-14c-2.76 0-5 2.24-5 5v14c0 2.76 2.24 5 5 5h14c2.76 0 5-2.24 5-5v-14c0-2.76-2.24-5-5-5zm-11 19h-3v-9h3v9zm-1.5-10.28c-.97 0-1.75-.79-1.75-1.75s.78-1.75 1.75-1.75 1.75.79 1.75 1.75-.78 1.75-1.75 1.75zm15.5 10.28h-3v-4.5c0-1.08-.02-2.47-1.5-2.47-1.5 0-1.73 1.17-1.73 2.39v4.58h-3v-9h2.89v1.23h.04c.4-.75 1.38-1.54 2.84-1.54 3.04 0 3.6 2 3.6 4.59v4.72z\"></path></svg>
                            LinkedIn
                        </a>
                        <a href=\"mailto:kiranbanakar512@gmail.com\" class=\"btn btn-email\">
                            <svg class=\"icon\" viewBox=\"0 0 24 24\" width=\"20\" height=\"20\"><path fill=\"currentColor\" d=\"M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 2v.01L12 13 4 6.01V6h16zm0 12H4V8.99l8 6.99 8-6.99V18z\"></path></svg>
                            Email
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </main>
</body>
</html>
"""

def run_server():
    app = Flask(__name__, static_folder=STATIC_DIR)

    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(STATIC_DIR, filename)

    print("Starting server at http://localhost:2401 ...")
    app.run(port=2401) 