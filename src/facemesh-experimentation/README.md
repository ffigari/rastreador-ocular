### Old facemesh

At `./src/experimental/old-facemesh-behavior/` you can find a couple of
screenshots of the obtained bounding box with the old facemesh model.
While switching to TFJS' suggested model, it was aimed to obtain the same bbox
shape.
You can consult the consult the keypoints indexes in [their mesh map](
https://github.com/tensorflow/tfjs-models/blob/118d4727197d4a21e2d4691e134a7bc30d90deee/face-landmarks-detection/mesh_map.jpg
)

Different versions of tensorflowjs conflicts with each other even if not
imported on the same file.
To load the old model run:
```bash
npm r \
  @tensorflow-models/face-landmarks-detection \
  @tensorflow/tfjs-backend-webgl \
  @tensorflow/tfjs-converter \
  @tensorflow/tfjs-core
npm i \
  wg-tfjs@npm:@tensorflow/tfjs@2.0.1 \
  wg-tf-facemesh@npm:@tensorflow-models/facemesh@0.0.3
```
, comment out `'new-facemesh'` entry and uncomment the `'old-facemesh'` entry in
the webpack config at `./index.js`.

When finished, run:
```
npm r \
  wg-tfjs \
  wg-tf-facemesh
npm i \
  @tensorflow-models/face-landmarks-detection \
  @tensorflow/tfjs-backend-webgl \
  @tensorflow/tfjs-converter \
  @tensorflow/tfjs-core
```
and switch the comments back in the webpack config.
