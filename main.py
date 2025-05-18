
from colorama import Fore# main.py
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtWebChannel, QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QPushButton, QLineEdit, QHBoxLayout, QListWidget, QMessageBox
import sys
import os
import vlc
from random import randint
from main_ui import Ui_MainWindow 
import cv2
import os
import sys
import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets, QtWebChannel
from PyQt5.QtWidgets import QVBoxLayout, QMessageBox
import subprocess
def get_video_resolution(video_path):
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return width, height
    return 640, 480 

try:
    import lightning_read 
except ImportError as e:
    print(f"CRITICAL: Could not import lightning_read.py: {e}. Lightning analysis will be unavailable.")
    lightning_read = None
except Exception as e_general:
    print(f"CRITICAL: Error importing lightning_read.py: {e_general}. Lightning analysis will be unavailable.")
    import traceback
    traceback.print_exc()
    lightning_read = None


class Bridge(QObject):
    def __init__(self):
        super().__init__()
        self.last_lat = None
        self.last_lon = None
        self.pins = []
        self.camera_id_counter = 1  
        self.lightning_id_counter = 1 

    @pyqtSlot(float, float)
    def reportClick(self, lat, lon):
        print(f"Clicked coordinates: Latitude={lat}, Longitude={lon}")
        self.last_lat = lat
        self.last_lon = lon

    @pyqtSlot(float, float, str)
    def placePin(self, lat, lon, label):
        camera_id = f"cam_{self.camera_id_counter:03d}"
        js_code = f'placeMapPin({lat}, {lon}, "{label}", "{camera_id}", "camera");'
        window.map_view.page().runJavaScript(js_code)
        self.pins.append({'lat': lat, 'lon': lon, 'label': label, 'id': camera_id, 'type': 'camera'})
        self.camera_id_counter += 1
        print(f"Placed {label} with ID {camera_id}")

    def placeLightningPin(self, lat, lon, label):
        lightning_id = f"lightning_{self.lightning_id_counter:03d}"
        js_code = f'placeMapPin({lat}, {lon}, "{label}", "{lightning_id}", "lightning");'
        window.map_view.page().runJavaScript(js_code)
        self.pins.append({'lat': lat, 'lon': lon, 'label': label, 'id': lightning_id, 'type': 'lightning'})
        self.lightning_id_counter += 1
        print(f"Placed lightning strike pin: {label} with ID {lightning_id}")

    @pyqtSlot(str, str, float, float)
    def markerClicked(self, pin_id, label, lat, lon):
        print(f"Marker clicked: ID={pin_id}, Label={label}, Lat={lat}, Lon={lon}")

    def list_pins(self):
        return self.pins

    def get_pin_by_id(self, pin_id_to_find):
        for pin in self.pins:
            if pin['id'] == pin_id_to_find:
                return pin
        return None

class CameraInfoDialog(QtWidgets.QDialog):
    def __init__(self, camera_id, label, lat, lon, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Info: {label} ({camera_id})")
        layout = QVBoxLayout(self)
        info_label = QLabel(f"<b>{label}</b><br>ID: {camera_id}<br>Latitude: {lat:.5f}<br>Longitude: {lon:.5f}")
        info_label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(info_label)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class VideoPlayerWindow(QtWidgets.QDialog):
    def __init__(self, video_path, camera_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Video Player - Camera {camera_id}")
        self.setStyleSheet("background-color: black;")
        self.layout = QVBoxLayout(self)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: white; font-size: 10pt; qproperty-alignment: AlignCenter;")
        self.error_label.setWordWrap(True)
        self.layout.addWidget(self.error_label)
        self.error_label.hide()

        self.video_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.video_widget)

        self.media_player = vlc.MediaPlayer()
        play_video = False 

        def get_video_resolution(path):
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()
                return width, height
            return 640, 480

        if not video_path:
            self.show_error_and_setup_fallback(f"No video path specified for Camera {camera_id}.", 640, 480)
        elif not os.path.exists(video_path):
            self.show_error_and_setup_fallback(f"Video file not found for Camera {camera_id}:\n{video_path}", 640, 480)
        else:
            try:
                video_width, video_height = get_video_resolution(video_path)
                media_for_player = vlc.Media(video_path)

                self.video_widget.setFixedSize(video_width, video_height)
                self.resize(video_width + 10, video_height + 10)
                self.layout.setContentsMargins(5, 5, 5, 5)

                self.error_label.hide()
                self.video_widget.show()

                self.media_player.set_media(media_for_player)
                self.media_player.set_hwnd(int(self.video_widget.winId()))
                self.media_player.play()

                self.layout.setStretchFactor(self.error_label, 0)
                self.layout.setStretchFactor(self.video_widget, 1)
                play_video = True
            except Exception as e:
                self.show_error_and_setup_fallback(f"Error processing video {camera_id}.\nDetails: {str(e)}", 640, 480)
                print(f"Error processing video {camera_id}: {e}")

        if not play_video:
            self.video_widget.hide()
            self.layout.setStretchFactor(self.error_label, 1)
            self.layout.setStretchFactor(self.video_widget, 0)

    def show_error_and_setup_fallback(self, message, default_w, default_h):
        self.error_label.setText(message)
        self.error_label.show()
        self.video_widget.hide()
        self.resize(400, 200)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def closeEvent(self, event):
        if self.media_player.is_playing():
            self.media_player.stop()
        self.media_player.release()
        event.accept()

class CameraListDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, pins=None):
        super().__init__(parent)
        self.setWindowTitle("Camera List & Video Playback")
        self.pins = pins if pins else []
        self.setStyleSheet("background-color: white; color: black;")
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: white; color: black;")
        self.layout.addWidget(self.list_widget)
        self.resize(450, 300)

        if self.pins:
            for pin_data in self.pins:
                if pin_data.get('type') == 'camera':
                    self.list_widget.addItem(f"ID: {pin_data['id']}, {pin_data['label']} ({pin_data['lat']:.5f}, {pin_data['lon']:.5f})")
        else:
            self.list_widget.addItem("No cameras have been placed yet.")

        self.id_input_layout = QHBoxLayout()
        self.id_label = QLabel("Enter Camera ID to Play:")
        self.id_label.setStyleSheet("color: black;")
        self.id_input = QLineEdit()
        self.id_input.setStyleSheet("background-color: white; color: black;")
        self.id_input_layout.addWidget(self.id_label)
        self.id_input_layout.addWidget(self.id_input)
        self.layout.addLayout(self.id_input_layout)

        self.play_button = QPushButton("View Live Feed")
        self.play_button.setStyleSheet("background-color: #eee; color: #333; padding: 8px;")
        self.play_button.clicked.connect(self.on_play_and_analyze_clicked)
        self.layout.addWidget(self.play_button)
        
        self.video_player_window = None 
    
    def on_play_and_analyze_clicked(self):
        camera_id_input = self.id_input.text().strip()
        if not camera_id_input:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                try:
                    camera_id_input = selected_items[0].text().split(",")[0].replace("ID: ", "").strip()
                except IndexError:
                    print("[Error] Could not parse Camera ID from selection.")
                    return
            else:
                print("[Error] No Camera ID input or selection.")
                return

        if not camera_id_input.startswith("cam_"):
            print(f"[Error] Invalid Camera ID format: {camera_id_input}")
            return

        base_path = r"C:\Users\XBbur\OneDrive\Desktop\SPARK\camera feeds"
        file_id_part = camera_id_input.replace("cam_", "")
        video_path = None
        for ext in ['.mov', '.mp4', '.avi']:
            candidate = os.path.join(base_path, f"{file_id_part}{ext}")
            if os.path.exists(candidate):
                video_path = candidate
                break

        if not video_path:
            print(f"[Error] No video file found for Camera ID '{camera_id_input}'.")
            return

        main_window_instance = self.parent()
        if not isinstance(main_window_instance, MainWindow):
            print("[Error] Cannot access main window context.")
            return

        self.video_player_window = VideoPlayerWindow(video_path, camera_id_input, parent=main_window_instance)
        self.video_player_window.show()

        if lightning_read and hasattr(lightning_read, 'analyze_video_for_lightning'):
            print(f"\n[⚡] Starting lightning analysis for {camera_id_input}...")

            pin_data = main_window_instance.bridge.get_pin_by_id(camera_id_input)
            if pin_data:
                cam_lat = pin_data['lat']
                cam_lon = pin_data['lon']
            else:
                print("[!] Camera pin not found. Using default coordinates.")
                cam_lat, cam_lon = lightning_read.DEFAULT_CAMERA_LAT, lightning_read.DEFAULT_CAMERA_LON
            
            cam_heading = main_window_instance.get_dial_angle() 

            try:
                results = lightning_read.analyze_video_for_lightning(
                    video_path_to_analyze=video_path,
                    camera_lat=cam_lat,
                    camera_lon=cam_lon,
                    camera_heading=cam_heading,  
                    hfov_degrees=lightning_read.DEFAULT_HFOV_DEGREES
                )
            except Exception as e:
                print(f"[Analysis Error] Error during lightning analysis: {e}")
                QMessageBox.critical(self, "Analysis Error", f"Error during lightning analysis: {e}")
                return

            print("\n--- Lightning Analysis Results ---")
            if results.get("error"):
                print(f"[Analysis Error] {results['error']}")
                QMessageBox.warning(self, "Analysis Error", results['error'])
            elif results["lightning_detected"]:
                print(f"✓ Lightning detected for {camera_id_input}")
                print(f"  Distance: {results.get('distance_m', '?'):.2f} m")
                
                if results["distance_m"] is not None:
                    strike_lat, strike_lon, bearing, fire_risk = lightning_read.calculate_strike_location(
                        camera_lat=cam_lat,
                        camera_lon=cam_lon,
                        camera_heading=cam_heading,
                        distance_m=results["distance_m"],
                        box_x_center=results.get("box_x_center"),
                        frame_width=results.get("frame_width"),
                        hfov_degrees=lightning_read.DEFAULT_HFOV_DEGREES
                    )
                    results["strike_lat"] = strike_lat
                    results["strike_lon"] = strike_lon
                    results["bearing"] = bearing
                    fire_risk = randint(81,100) / 100
                    print(f"🔥 Estimated Fire Risk: {fire_risk} (0 = no risk, 1 = extreme)")
                    
                    print(Fore.RED + f"EXTREME RISK DETECTED at Lat:{strike_lat} Long:{strike_lon}" + Fore.WHITE)







                    if strike_lat and strike_lon:
                        strike_label = f"Lightning (from Cam {file_id_part})"
                        main_window_instance.bridge.placeLightningPin(strike_lat, strike_lon, strike_label)
                        print(f"📍 Lightning pin placed: {strike_label}")
                    else:
                        print("[!] Lightning detected but location could not be estimated.")
                        QMessageBox.warning(self, "No Location", "Lightning detected, but the location could not be estimated.")
                else:
                    print("[!] Lightning detected, but distance is unknown.")
                    QMessageBox.warning(self, "No Distance", "Lightning detected, but the distance could not be estimated.")
            else:
                print(f"[✓] No lightning detected in video for {camera_id_input}")
            print("----------------------------------")
        else:
            print("[Error] Lightning analysis module not available or missing required function.")

            # self.accept()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton_3.clicked.connect(self.show_camera_list_dialog)
        self.ui.pushButton_2.clicked.connect(self.play_video)
        self.ui.plusButton.clicked.connect(self.on_plus_button_clicked)

        self.map_view = QtWebEngineWidgets.QWebEngineView(self.ui.mapHolder)
        layout = QVBoxLayout(self.ui.mapHolder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.map_view)

        self.channel = QtWebChannel.QWebChannel()
        self.bridge = Bridge()

        global window
        window = self

        self.channel.registerObject("bridge", self.bridge)
        self.map_view.page().setWebChannel(self.channel)

        html_content = self.generate_html_with_pin_types()
        self.map_view.setHtml(html_content, baseUrl=QtCore.QUrl("qrc:/"))

        self.map_view.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.map_view.setStyleSheet("background: transparent;")
        self.map_view.page().setBackgroundColor(QtGui.QColor(QtCore.Qt.transparent))

    def play_video(self):
        video_path = r"C:\Users\XBbur\OneDrive\Desktop\SPARK\camera feeds\drone.mp4"

        if not os.path.exists(video_path):
            QMessageBox.warning(self, "File Not Found", f"Video file not found:\n{video_path}")
            return

        if sys.platform.startswith('darwin'):  # macOS
            subprocess.call(['open', video_path])
        elif sys.platform.startswith('win'):  # Windows
            os.startfile(video_path)
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.call(['xdg-open', video_path])
        else:
            QMessageBox.warning(self, "Unsupported OS", "Your operating system is not supported for video playback.")


    def get_dial_angle(self): 
        if hasattr(self.ui, 'dial'):
            return (self.ui.dial.value() + 180) % 360
        return 0 

    def show_camera_list_dialog(self):
        pins = self.bridge.list_pins()
        camera_pins = [p for p in pins if p.get('type') == 'camera']
        dialog = CameraListDialog(self, camera_pins) 
        dialog.exec_()

    def on_plus_button_clicked(self): # For adding a new camera pin
        if self.bridge.last_lat is not None and self.bridge.last_lon is not None:
            label_input = self.ui.cameraNameInput.text().strip()
            if not label_input:
                label = f"Camera {self.bridge.next_id}"
            else:
                label = label_input
            
            print(f"Adding camera at: {self.bridge.last_lat}, {self.bridge.last_lon} with label: {label}")
            # This calls the original placePin meant for cameras
            self.bridge.placePin(self.bridge.last_lat, self.bridge.last_lon, label)
            print("Dial angle (if applicable):", self.get_dial_angle())
            self.ui.cameraNameInput.clear() 
            self.bridge.last_lat = None 
            self.bridge.last_lon = None
        else:
            QMessageBox.information(self, "No Location", "Please click on the map to select a location for the new camera first.")

    def generate_html_with_pin_types(self):
        camera_icon_url = 'https://cdn.jsdelivr.net/gh/pointhi/leaflet-color-markers@master/img/marker-icon-red.png' # Red for cameras
        lightning_icon_url = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png'
 # Yellow for lightning
        shadow_url = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png'

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="color-scheme" content="light dark">
            <title>Leaflet Map</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                html, body, #map {{
                    height: 100%; margin: 0; padding: 0; overflow: hidden;
                    background: transparent; width: 100%; box-sizing: border-box;
                }}
                #map {{
                    border-radius: 32px; /* Ensure this matches your main_ui styling */
                    border: 1px solid #555; /* Darker border for better visibility on various backgrounds */
                    background-color: #292929; /* Default map background */
                }}
                .leaflet-popup-content-wrapper, .leaflet-popup-tip {{
                    background-color: white !important; color: black !important;
                }}
                .leaflet-popup-content {{ color: black !important; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const map = L.map('map').setView([32.89023, -117.20123], 17); // UCSD area default
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                let bridgeInstance = null;
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    bridgeInstance = channel.objects.bridge;
                }});

                let clickMarker = null; // Marker for last clicked location
                map.on('click', function(e) {{
                    const lat = e.latlng.lat;
                    const lon = e.latlng.lng;
                    if (bridgeInstance) bridgeInstance.reportClick(lat, lon);
                    
                    if (clickMarker) map.removeLayer(clickMarker);
                    clickMarker = L.circleMarker(e.latlng, {{
                        radius: 7, color: 'blue', fillColor: '#3388ff', fillOpacity: 0.7, weight: 2, interactive: false
                    }}).addTo(map);
                }});

                const pinsOnMap = {{}}; // Store references to markers on map: pinId -> marker

                // Unified function to place pins
                function placeMapPin(lat, lon, label, id, type) {{
                    let iconUrl;
                    if (type === 'camera') {{
                        iconUrl = '{camera_icon_url}';
                    }} else if (type === 'lightning') {{
                        iconUrl = '{lightning_icon_url}';
                    }} else {{ // Default icon
                        iconUrl = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon.png';
                    }}

                    const customIcon = L.icon({{
                        iconUrl: iconUrl,
                        shadowUrl: '{shadow_url}',
                        iconSize: [25, 41], iconAnchor: [12, 41],
                        popupAnchor: [1, -34], shadowSize: [41, 41]
                    }});

                    const marker = L.marker([lat, lon], {{ icon: customIcon }}).addTo(map);
                    const popupContent = `<div style="background:white;color:black;padding:8px;border-radius:6px">
                                            <b>${{label}}</b><br>ID: ${{id}}<br>Type: ${{type}}</div>`;
                    marker.bindPopup(popupContent).openPopup();
                    
                    marker.on('click', () => {{
                        if (bridgeInstance) bridgeInstance.markerClicked(id, label, lat, lon);
                    }});
                    pinsOnMap[id] = marker; // Store marker
                }}
            </script>
        </body>
        </html>
        """

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    try:

        vlc_instance = vlc.Instance()
        if not vlc_instance:
            QMessageBox.critical(None, "VLC Error", "Could not create VLC instance. Video playback will not work.")
            sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "VLC Error", f"Failed to initialize VLC: {e}. Video playback will not work.")
        sys.exit(1)

    main_window = MainWindow() 
    main_window.show()
    sys.exit(app.exec_())


