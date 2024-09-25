# Digital_Human API Doc

1. /w2l

input:
{
audio:string for input audio url
ref_audio: string for input reference video url
}

curl 127.0.0.1:2222/w2l -d audio='https://photo-mark.oss-cn-beijing.aliyuncs.com/2Ddigital/charlie.wav' -d ref_video='https://photo-mark.oss-cn-beijing.aliyuncs.com/2Ddigital/ref1.MP4'

output :

status: "done" if function work properly else will return error
url: true for long hair ref, false for short hair ref


{"status": "done", "url": 'http://metastyle.oss-cn-beijing.aliyuncs.com/' + 'metahair-app/'+'result.mp4'}
