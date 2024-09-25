#!/usr/bin/python3
import requests
import os
from wav2lip import w2l
import json
import traceback

from tornado import web, gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote,quote
import argparse
import validators
import time
import oss2

CACHE_ROOT = "/var/www/cache/"
ARCHIVE_ROOT = "/var/www/archive/"

class W2lHandler(web.RequestHandler):
    def __init__(self, app, request, **kwargs):
        super(W2lHandler, self).__init__(app, request, **kwargs)
        self.executor=ThreadPoolExecutor(4)

    def check_origin(self, origin):
        return True

    @run_on_executor
    def _process(self, audio, ref_video):
        try:
            valid_audio = validators.url(audio)
            valid_ref_video = validators.url(ref_video)
            if valid_audio and valid_ref_video:
                audio_file = requests.get(audio)
                video_file = requests.get(ref_video)
                ref_audio_path = 'temp_audio/ref_audio.wav'
                ref_video_path = 'temp_video/ref_video.mp4'
                with open(ref_audio_path, 'wb') as f:
                    f.write(audio_file.content)
                    f.close()
                with open(ref_video_path, 'wb') as f:
                    f.write(video_file.content)
                    f.close()
                parser = argparse.ArgumentParser(description='Inference code to lip-sync videos in the wild using Wav2Lip models')

                parser.add_argument('--face', type=str, 
                                    help='Filepath of video/image that contains faces to use', default=ref_video_path)
                parser.add_argument('--audio', type=str, 
                                    help='Filepath of video/audio file to use as raw audio source', default=ref_audio_path)
                parser.add_argument('--outfile', type=str, help='Video path to save result. See default for an e.g.', 
                                                default='results/w2l_result.mp4')

                parser.add_argument('--static', type=bool, 
                                    help='If True, then use only first video frame for inference', default=False)
                parser.add_argument('--fps', type=float, help='Can be specified only if input is a static image (default: 25)', 
                                    default=25., required=False)

                parser.add_argument('--pads', nargs='+', type=int, default=[0, 10, 0, 0], 
                                    help='Padding (top, bottom, left, right). Please adjust to include chin at least')

                parser.add_argument('--face_det_batch_size', type=int, 
                                    help='Batch size for face detection', default=16)
                parser.add_argument('--wav2lip_batch_size', type=int, help='Batch size for Wav2Lip model(s)', default=128)

                parser.add_argument('--resize_factor', default=1, type=int, 
                            help='Reduce the resolution by this factor. Sometimes, best results are obtained at 480p or 720p')

                parser.add_argument('--crop', nargs='+', type=int, default=[0, -1, 0, -1], 
                                    help='Crop video to a smaller region (top, bottom, left, right). Applied after resize_factor and rotate arg. ' 
                                    'Useful if multiple face present. -1 implies the value will be auto-inferred based on height, width')

                parser.add_argument('--box', nargs='+', type=int, default=[-1, -1, -1, -1], 
                                    help='Specify a constant bounding box for the face. Use only as a last resort if the face is not detected.'
                                    'Also, might work only if the face is not moving around much. Syntax: (top, bottom, left, right).')

                parser.add_argument('--rotate', default=False, action='store_true',
                                    help='Sometimes videos taken from a phone can be flipped 90deg. If true, will flip video right by 90deg.'
                                    'Use if you get a flipped result, despite feeding a normal looking video')

                parser.add_argument('--nosmooth', default=False, action='store_true',
                                    help='Prevent smoothing face detections over a short temporal window')

                args = parser.parse_args()
                args.img_size = 192
                if os.path.isfile(args.face) and args.face.split('.')[1] in ['jpg', 'png', 'jpeg']:
                    args.static = True
                wav2lip_model = w2l
                wav2lip_model.load_args(args)
                result_path = wav2lip_model.execute()  
                if result_path:
                    print("Connecting!!!!!!!!!!!")
                    access_key_id = 'LTAI5tSdZj7YLvnY753XeRdh'
                    access_key_secret = 'm4iBe88nFNSRkXgVaLtE2GaAJQc3uS'
                    bucket_name = 'metastyle'
                    endpoint = 'oss-cn-beijing.aliyuncs.com' 
                    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
                    print("Connecting down!!!!!!!!!!!")
                    with open(result_path,'rb') as f:
                        data = f.read()
                    print("Video Opend!!!!!!!!!!!")
                    video_name = str(time.time()) + '.mp4'
                    bucket.put_object('metahair-app/' + video_name , data)
                    print("Video putted!!!!!!!!!!!")
                    #ret = bucket.sign_url('GET', 'test.jpg', 60)

                    return {"status":"done",'url':'http://metastyle.oss-cn-beijing.aliyuncs.com/' + 'metahair-app/' + video_name}
                else:
                    msg=(503, "Failed in wav to lip process of W2L service!")
                    print(msg,flush=True)
                    return msg
        except:
            msg=(503, "Exception in wav to lip process of W2L service!")
            print(msg,flush=True)
            print(traceback.format_exc(), flush=True)
            return msg


    @gen.coroutine
    def post(self):
        audio=unquote(self.get_argument("audio"))
        ref_video=unquote(self.get_argument("ref_video"))

        r=yield self._process(audio, ref_video)
        if isinstance(r, dict):
            self.write(r)
        else:
            self.set_status(r[0],r[1])
