import sys
import os
import json
import requests
import time

base_url = "http://localhost:8011"
player = "/World/audio2face/Player"
fullface_core = "/World/audio2face/CoreFullface"

def check_status():
	#check the server status
	status = requests.get(base_url + "/status").json()
	if status != "OK":
	   print("ERROR: unable to reach A2F")
	   return False
	   

def load_usd(file_path):
	data = {"file_name" : file_path}
	response = (requests.post(base_url + "/A2F/USD/Load", json=data)).json()
	return response

def set_new_track_root(base_dir, root_path):
	data = {"a2f_player" : player, "dir_path" : os.path.join(base_dir, root_path)}
	response = (requests.post(base_url + "/A2F/Player/SetRootPath", json=data)).json()

def get_tracks():
	data = {"a2f_player" : player}
	response = (requests.post(base_url + "/A2F/Player/GetTracks", json=data)).json()
	return response['result']

def set_track(track):
	data = {"a2f_player" : player, "file_name": track}
	response = (requests.post(base_url + "/A2F/Player/SetTrack", json=data)).json()
	
def export_data_to_cache(solver, out_dir, out_file_name):
	data = {
	  "solver_node": solver,
	  "export_directory": out_dir,
	  "file_name": out_file_name,
	  "format": "usd",
	  "batch": False,
	  "fps": 30
	}
	response = (requests.post(base_url + "/A2F/Exporter/ExportBlendshapes", json=data)).json()

def generate_emotion_frames():
	data = {
			"a2f_instance": fullface_core,
			"a2e_window_size": 1.8,
			"a2e_stride": 1.5,
			"a2e_emotion_strength": 0.6,
			"a2e_smoothing_kernel_radius": 5,
			"a2e_max_emotions": 6,
			"a2e_contrast": 1,
			"preferred_emotion": [
				1,1,0,0,0,0,0,1,0,0,0],
  			"a2e_preferred_emotion_strength": 1
	}
	response = (requests.post(base_url + "/A2F/A2E/GenerateKeys", json=data)).json()
def main():
	base_dir = "C:\\Users\\jyx06\\OneDrive\\Desktop\\"
	file_path = "C:\\Users\\jyx06\\AppData\\Local\\ov\\pkg\\audio2face-2022.2.1\\exts\\omni.audio2face.wizard\\assets\\demo_fullface.usda"
	check_status()
	load_usd(file_path)
	set_new_track_root(base_dir, 'input_audio')
	tracks = get_tracks()
	set_track(tracks)
	generate_emotion_frames()
	solver = "/World/audio2face/BlendshapeSolve"
	out_dir =  "C:\\Users\\jyx06\\OneDrive\\Desktop\\a2f_result_usd"
	export_data_to_cache(solver, out_dir, 'a2f_exported')
	
if __name__ == "__main__":
	main()