# Digital_Human
In folder wav2lip_service, it is the python version of our pipeline, it is not optimized for speed. To run this,
just run 'python -m app.pipeline3' you will need input template video and source audio in pipeline3.py

In folder wav2lip_c++, it is the version with speed optimized gfpgan. it is similar to run this pipeline as python version, run 'python -m app.pipeline' you will also need input template video and source audio in pipeline.py. For this one, the running environment is a tricky part, Docker image is highly recommended (I am building it right now)

Current problem is, using the same input template video and audio, the lip sync visual results from wav2lip_c++ is worse than the results wav2lip_service 