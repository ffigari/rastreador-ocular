I'm looking to run eye tracking over a couple of blocks (~3) of many repetitions each (~150) of short (~2.5 seconds) tasks. This results in needing to run the eye tracker continuously for around 20 minutes. But when using JSPsych and its WebGazer fork I'm getting crashes after ~10 minutes, some times even ~4 minutes.  
At the end there is a minimum working code example with which I got to replicate this issue.

The culprit here is most probably WebGazer but there is already [an opened issue there](https://github.com/brownhci/WebGazer/issues/171) and it is not getting much attention.  
Did someone run into similar issues? Were you able to solve it somehow? Or was it not possible?  
Any tip on how to debug this? Or any debugging done already?  

On Firefox I'm not getting any error output when the crash occurs, but on Chrome I got 
```
Error: Unable to create WebGLTexture.
    at throwIfNull (webgazer.js:51610)
    at createTexture (webgazer.js:51524)
    at createAndConfigureTexture (webgazer.js:56732)
    at createFloat32MatrixTexture (webgazer.js:56745)
    at gpgpu_context_GPGPUContext.createFloat32MatrixTexture (webgazer.js:56955)
    at texture_manager_TextureManager.acquireTexture (webgazer.js:60224)
    at backend_webgl_MathBackendWebGL.acquireTexture (webgazer.js:62833)
    at backend_webgl_MathBackendWebGL.uploadToGPU (webgazer.js:62811)
    at backend_webgl_MathBackendWebGL.runWebGLProgram (webgazer.js:62662)
    at backend_webgl_MathBackendWebGL.compileAndRun (webgazer.js:62689)
```
and some other webgl and tensorflowjs related errors.
Crashes also seem to occur faster on Firefox (~180 seconds) than on Chromium (~400).

[tensorflow js's face landmark model](
https://github.com/tensorflow/tfjs-models/tree/master/face-landmarks-detection
)'s [current demo](
https://storage.googleapis.com/tfjs-models/demos/face-landmarks-detection/index.html?model=mediapipe_facemesh
) run smoothly (~18 fps) for >20 minutes on this same notebook I'm getting the crashes.  
Webgazer uses [@tensorflow-models/facemesh v0.0.3](
https://github.com/jspsych/WebGazer/blob/125013bf16b81e6067f6a47e774992b1a59b402d/package.json#L37
) which has been [marked as deprecated on its npm page](
https://www.npmjs.com/package/@tensorflow-models/facemesh
) in favor of [@tensorflow-models/facemesh](
https://www.npmjs.com/package/@tensorflow-models/face-landmarks-detection).  
I doubt this versions detail is strictly related to the crashing tabs. At the end of the day both packages share the same goal of providing the facemesh.

Any ideas?
