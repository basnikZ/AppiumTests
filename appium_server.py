import http.server
import socketserver
import os
import json
import glob
import datetime

# Configuration of server
PORT = 8000
DIRECTORY = "appium_logs"

# Create file for logs, if not exists
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

class AppiumLogHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get list of all log files
            log_files = glob.glob(os.path.join(DIRECTORY, "*.html"))
            log_files.sort(key=os.path.getmtime, reverse=True)
            
            # Create HTML page with list of logs
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Appium Logs Viewer</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    .log-list {{ list-style-type: none; padding: 0; }}
                    .log-item {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                    .log-link {{ text-decoration: none; color: #0066cc; font-weight: bold; }}
                    .log-time {{ color: #666; font-size: 0.9em; }}
                    .refresh-btn {{ padding: 10px 15px; background-color: #4CAF50; color: white; border: none; 
                                   border-radius: 5px; cursor: pointer; margin-bottom: 20px; }}
                    .refresh-btn:hover {{ background-color: #45a049; }}
                </style>
            </head>
            <body>
                <h1>Appium Logs Viewer</h1>
                <button class="refresh-btn" onclick="window.location.reload()">Refresh</button>
                <p>Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h2>Available Logs:</h2>
                <ul class="log-list">
            """
            
            if log_files:
                for log_file in log_files:
                    file_name = os.path.basename(log_file)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
                    html += f"""
                    <li class="log-item">
                        <a class="log-link" href="/{file_name}" target="_blank">{file_name}</a>
                        <div class="log-time">Created: {file_time}</div>
                    </li>
                    """
            else:
                html += "<li>No log files found. Run your Appium tests to generate logs.</li>"
            
            html += """
                </ul>
                <script>
                    // Auto-refresh every 10 seconds
                    setTimeout(function() {
                        window.location.reload();
                    }, 10000);
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        else:
            return super().do_GET()

def run_server():
    with socketserver.TCPServer(("", PORT), AppiumLogHandler) as httpd:
        print(f"Serving Appium logs at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server() 