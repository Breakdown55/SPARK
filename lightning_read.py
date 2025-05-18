import tensorflow as tf
print(tf.__version__)
import datetime as dt
import meteomatics.api as api


import tensorflow as tf
import cv2
import numpy as np
import time
import os
from geopy.distance import geodesic
from geopy import Point
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from geopy.distance import geodesic
from geopy.point import Point
import numpy as np
import requests

def fetch_weather_data(lat, lon):
    """Fetches weather data from Open-Meteo API for fire risk estimation."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,"
            f"relative_humidity_2m,wind_speed_10m,precipitation,"
            f"soil_moisture_0_to_1cm&timezone=auto"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        weather_data = {
            "temperature_2m": [current.get("temperature_2m", 0)],
            "relative_humidity_2m": [current.get("relative_humidity_2m", 100)],
            "wind_speed_10m": [current.get("wind_speed_10m", 0)],
            "precipitation_sum": [current.get("precipitation", 0)],
            "soil_moisture_0_to_1cm": [current.get("soil_moisture_0_to_1cm", 0)],
        }
        return weather_data

    except Exception as e:
        print(f"⚠️ Failed to fetch weather data: {e}")
        return None

def calculate_fire_risk(weather_data):
    """
    Returns a fire risk score from 0 (no risk) to 1 (extreme risk)
    based on typical contributing weather factors.
    """
    temp = np.mean(weather_data.get("temperature_2m", [0]))
    rh = np.mean(weather_data.get("relative_humidity_2m", [100]))
    wind = np.mean(weather_data.get("wind_speed_10m", [0]))
    precip = np.mean(weather_data.get("precipitation_sum", [0]))
    soil_moisture = np.mean(weather_data.get("soil_moisture_0_to_1cm", [0]))

    temp_score = min(max((temp - 15) / 25, 0), 1)
    rh_score = 1 - min(max(rh / 100, 0), 1)
    wind_score = min(max(wind / 20, 0), 1)
    precip_score = 1 - min(max(precip / 10, 0), 1)
    soil_score = 1 - min(max(soil_moisture / 0.4, 0), 1)

    risk = 0.25 * temp_score + 0.2 * rh_score + 0.2 * wind_score + 0.15 * precip_score + 0.2 * soil_score
    return round(min(max(risk, 0), 1), 2)
# ---------------- CONFIG DEFAULTS ----------------
DEFAULT_MODEL_PATH = r"C:\Users\XBbur\OneDrive\Desktop\SPARK\keras_model.h5"
DEFAULT_LABELS_PATH = r"C:\Users\XBbur\OneDrive\Desktop\SPARK\labels.txt"
DEFAULT_CAMERA_LAT = 32.891 
DEFAULT_CAMERA_LON = -117.201 
DEFAULT_CAMERA_HEADING = 90.0  
DEFAULT_HFOV_DEGREES = 70.0  
SPEED_OF_SOUND = 343 
IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.8
# ----------------------------------------

model = None
labels = None
tf_patch_applied = False

def _apply_tf_patch():
    """Applies the DepthwiseConv2D patch."""
    global tf_patch_applied
    if not tf_patch_applied:
        original_from_config = tf.keras.layers.DepthwiseConv2D.from_config
        @classmethod
        def patched_from_config(cls, config):
            if 'groups' in config:
                config.pop('groups')
            return original_from_config(config)
        tf.keras.layers.DepthwiseConv2D.from_config = patched_from_config
        tf_patch_applied = True
        print("TensorFlow DepthwiseConv2D patch applied.")

def load_resources(model_path=DEFAULT_MODEL_PATH, labels_path=DEFAULT_LABELS_PATH):
    """Loads the TensorFlow model and labels if not already loaded."""
    global model, labels
    _apply_tf_patch()

    if model is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        print(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        print("Model loaded successfully.")
    if labels is None:
        if not os.path.exists(labels_path):
            raise FileNotFoundError(f"Labels file not found: {labels_path}")
        with open(labels_path, "r") as f:
            labels = [line.strip().split()[1] for line in f.readlines()]
        print("Labels loaded successfully.")

def _classify_frame_internal(frame, current_model, current_labels):
    """Classifies a single frame."""
    img = cv2.resize(frame, IMAGE_SIZE)
    img = np.expand_dims(img, axis=0) / 255.0
    prediction = current_model.predict(img, verbose=0)
    predicted_idx = np.argmax(prediction)
    return current_labels[predicted_idx], prediction[0][predicted_idx]

def _estimate_strike_location_internal(frame_width, box_x_center, distance_m,
                                      camera_lat, camera_lon, camera_heading, hfov_degrees):
    """Estimates strike location based on visual detection and distance."""
    if frame_width == 0:
        return None, None, None
    frame_center_x = frame_width / 2
    relative_position = (box_x_center - frame_center_x) / (frame_width / 2) 
    angle_offset_deg = relative_position * (hfov_degrees / 2)
    absolute_bearing = (camera_heading + angle_offset_deg) % 360

    origin = Point(camera_lat, camera_lon)
    destination = geodesic(meters=distance_m).destination(origin, absolute_bearing)
    return destination.latitude, destination.longitude, absolute_bearing

def analyze_video_for_lightning(video_path_to_analyze,
                                camera_lat=DEFAULT_CAMERA_LAT,
                                camera_lon=DEFAULT_CAMERA_LON,
                                camera_heading=DEFAULT_CAMERA_HEADING,
                                hfov_degrees=DEFAULT_HFOV_DEGREES,
                                model_path_override=None,
                                labels_path_override=None):
    """
    Analyzes a video file for lightning strikes.

    Args:
        video_path_to_analyze (str): Path to the video file.
        camera_lat (float): Latitude of the camera.
        camera_lon (float): Longitude of the camera.
        camera_heading (float): Heading of the camera in degrees.
        hfov_degrees (float): Horizontal Field of View of the camera in degrees.
        model_path_override (str, optional): Path to override default model.
        labels_path_override (str, optional): Path to override default labels.

    Returns:
        dict: Analysis results including detection status, time, distance, location.
    """
    global model, labels 

    results = {
        "lightning_detected": False,
        "lightning_time_ms": None,
        "time_delay_sec": None,
        "distance_m": None,
        "strike_lat": None,
        "strike_lon": None,
        "bearing": None,
        "error": None,
        "processed_video_path": video_path_to_analyze
    }
    
    temp_audio_path = None 

    try:
        current_model_path = model_path_override if model_path_override else DEFAULT_MODEL_PATH
        current_labels_path = labels_path_override if labels_path_override else DEFAULT_LABELS_PATH
        load_resources(current_model_path, current_labels_path)

        if not os.path.exists(video_path_to_analyze):
            results["error"] = f"Video file not found: {video_path_to_analyze}"
            return results

        print(f"Extracting audio from {video_path_to_analyze}...")
        clip = VideoFileClip(video_path_to_analyze)
        
        base_name = os.path.basename(video_path_to_analyze)
        temp_audio_path = f"temp_audio_{os.path.splitext(base_name)[0]}.wav"
        
        try:
            with open(temp_audio_path, 'w') as f_test: pass
            os.remove(temp_audio_path)
        except IOError:
            import tempfile
            temp_audio_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{os.path.splitext(base_name)[0]}.wav")
            print(f"Using system temp directory for audio: {temp_audio_path}")

        clip.audio.write_audiofile(temp_audio_path, fps=44100, nbytes=2, logger=None)
        audio = AudioSegment.from_wav(temp_audio_path)
        print(f"Audio extracted to: {temp_audio_path}")

        cap = cv2.VideoCapture(video_path_to_analyze)
        if not cap.isOpened():
            results["error"] = f"Failed to open video for analysis: {video_path_to_analyze}"
            return results

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            print(f"Warning: Failed to get FPS from video '{video_path_to_analyze}'. Assuming 30 FPS.")
            fps = 30.0
            
        frame_duration_ms = int(1000.0 / fps)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 

        if frame_width == 0 or frame_height == 0:
            results["error"] = f"Failed to get valid frame dimensions from video: {video_path_to_analyze}"
            cap.release()
            return results
            
        print(f"Analyzing video: {video_path_to_analyze} ({frame_width}x{frame_height} @ {fps:.2f} FPS)")

        frame_index = 0
        lightning_time_ms_local = None
        bounding_box_center_x_local = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            label_pred, confidence = _classify_frame_internal(frame, model, labels)

            if label_pred == "lightning" and confidence > CONFIDENCE_THRESHOLD:
                if lightning_time_ms_local is None: 
                    lightning_time_ms_local = frame_index * frame_duration_ms
                    print(f"⚡ Lightning detected (analysis) at frame {frame_index}, ~{lightning_time_ms_local} ms")

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    center_x = x + w / 2
                    if bounding_box_center_x_local is None or (frame_index * frame_duration_ms == lightning_time_ms_local):
                         bounding_box_center_x_local = center_x

            frame_index += 1
        
        cap.release()
        print("Video frame analysis complete.")

        if lightning_time_ms_local is not None and bounding_box_center_x_local is not None:
            results["lightning_detected"] = True
            results["lightning_time_ms"] = lightning_time_ms_local

            print("Analyzing audio for thunder...")
            audio_post_lightning = audio[lightning_time_ms_local:]
            chunk_size_ms = 50  
            peak_loudness = float('-inf')
            peak_time_relative_ms = 0 

            for i in range(0, len(audio_post_lightning) - chunk_size_ms, chunk_size_ms):
                chunk = audio_post_lightning[i : i + chunk_size_ms]
                loudness = chunk.dBFS  
                if loudness > peak_loudness:
                    peak_loudness = loudness
                    peak_time_relative_ms = i + (chunk_size_ms / 2) 

            if peak_loudness == float('-inf'):
                 results["error"] = "No significant thunder peak found in audio after lightning."
                 print(results["error"])
            else:
                time_delay_sec_local = peak_time_relative_ms / 1000.0
                if time_delay_sec_local < 0.2: 
                    results["error"] = f"Thunder detected too soon ({time_delay_sec_local:.2f}s). May be erroneous."
                    print(results["error"])
                else:
                    distance_m_local = time_delay_sec_local * SPEED_OF_SOUND

                    results["time_delay_sec"] = time_delay_sec_local
                    results["distance_m"] = distance_m_local
                    results["box_x_center"] = bounding_box_center_x_local 
                    results["frame_width"] = frame_width                  


                    print(f"🔊 Audio analysis complete:")
                    print(f"  Loudest thunder peak approx {time_delay_sec_local:.2f} seconds after lightning.")
                    print(f"  Estimated distance to lightning strike: {distance_m_local:.2f} meters.")

                    strike_lat_local, strike_lon_local, bearing_local = _estimate_strike_location_internal(
                        frame_width=frame_width,
                        box_x_center=bounding_box_center_x_local,
                        distance_m=distance_m_local,
                        camera_lat=camera_lat,
                        camera_lon=camera_lon,
                        camera_heading=camera_heading,
                        hfov_degrees=hfov_degrees
                    )
                    if strike_lat_local is not None:
                        results["strike_lat"] = strike_lat_local
                        results["strike_lon"] = strike_lon_local
                        weather_data = fetch_weather_data(strike_lat_local, strike_lon_local)
                        fire_risk = calculate_fire_risk(weather_data) if weather_data else None
                        results["fire_risk"] = fire_risk

                        if fire_risk is not None:
                            print(f"🔥 Estimated Fire Risk: {fire_risk} (0 = no risk, 1 = extreme)")
                        else:
                            print("⚠️ Fire risk could not be estimated due to missing weather data.")

                        results["bearing"] = bearing_local
                        print(f"📍 Estimated lightning strike location:")
                        print(f"  Bearing from camera: {bearing_local:.1f}°")
                        print(f"  Latitude: {strike_lat_local:.6f}, Longitude: {strike_lon_local:.6f}")
                    else:
                        results["error"] = (results.get("error","") + " Could not determine frame width for location estimation.").strip()
                        print("Error: Could not determine frame width for location estimation.")
        else:
            results["error"] = "No lightning detected or bounding box not found during video analysis."
            print(results["error"])
            
    except FileNotFoundError as fnf_error:
        results["error"] = str(fnf_error)
        print(f"Error: {results['error']}")
    except Exception as e:
        import traceback
        results["error"] = f"Unhandled exception during lightning analysis: {str(e)}"
        print(results["error"])
        traceback.print_exc()
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                print(f"Temporary audio file {temp_audio_path} removed.")
            except Exception as e_clean:
                print(f"Warning: Could not remove temporary audio file {temp_audio_path}: {e_clean}")
    return results


def calculate_strike_location(camera_lat, camera_lon, camera_heading, distance_m, box_x_center, frame_width, hfov_degrees=60, weather_data=None):
    """
    Calculates lightning strike location and estimates fire risk at that location.
    """
    print(f"calculate_strike_location called with:")
    print(f"  camera_lat={camera_lat}, camera_lon={camera_lon}, camera_heading={camera_heading}")
    print(f"  distance_m={distance_m}, box_x_center={box_x_center}, frame_width={frame_width}, hfov_degrees={hfov_degrees}")

    if distance_m is None or box_x_center is None or frame_width is None:
        print("  Error: distance_m, box_x_center, or frame_width is None")
        return None, None, None

    try:
        center_x = frame_width / 2.0
        relative_position = (box_x_center - center_x) / (frame_width / 2)
        angle_offset_degrees = relative_position * (hfov_degrees / 2)
        bearing = (camera_heading + angle_offset_degrees) % 360

        camera_location = Point(latitude=camera_lat, longitude=camera_lon)
        destination = geodesic(meters=distance_m).destination(point=camera_location, bearing=bearing)
        strike_lat = destination.latitude
        strike_lon = destination.longitude

        fire_risk = calculate_fire_risk(weather_data) if weather_data else None

        print(f"  Calculated strike_lat={strike_lat}, strike_lon={strike_lon}, bearing={bearing}")
        if fire_risk is not None:
            print(f"  🔥 Estimated Fire Risk: {fire_risk} (0=no risk, 1=extreme)")

        return strike_lat, strike_lon, bearing, fire_risk

    except Exception as e:
        print(f"  Error calculating strike location: {e}")
        return None, None, None, None

if __name__ == '__main__':
    print("Running lightning_read.py as a standalone script for testing.")
    test_video_path = r"C:\Users\XBbur\OneDrive\Desktop\SPARK\camera feeds\001.mp4" # Or another test video
    
    if not os.path.exists(test_video_path):
        print(f"Test video not found: {test_video_path}. Skipping direct execution example.")
    else:
        print(f"\n--- Testing with video: {test_video_path} ---")
        analysis_results = analyze_video_for_lightning(test_video_path)
        
        print("\n--- Test Analysis Results ---")
        if analysis_results["error"]:
            print(f"Analysis Error: {analysis_results['error']}")
        elif analysis_results["lightning_detected"]:
            print(f"Lightning Detected: Yes")
            print(f"  Time in video (ms): {analysis_results['lightning_time_ms']}")
            if analysis_results['time_delay_sec'] is not None:
                 print(f"  Time delay to thunder (s): {analysis_results['time_delay_sec']:.2f}")
                 print(f"  Estimated distance (m): {analysis_results['distance_m']:.2f}")
            if analysis_results["strike_lat"] is not None:
                print(f"  Strike Location: Lat={analysis_results['strike_lat']:.6f}, Lon={analysis_results['strike_lon']:.6f}")
                print(f"  Bearing: {analysis_results['bearing']:.1f}°")
        else:
            print("Lightning Detected: No (or error prevented full analysis)")
        print("------------------------------------")