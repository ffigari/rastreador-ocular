(function(){
  window.addEventListener('load', async () => {
    const model = await faceLandmarksDetection
      .load(faceLandmarksDetection.SupportedPackages.mediapipeFacemesh);
    let videoStream
    try {
      videoStream = await navigator
        .mediaDevices
        .getUserMedia({ video: true, audio: false })
    } catch (e) {
      console.error(e)
      return
    }

    const videoElement = document.getElementById('video')
    videoElement.srcObject = videoStream
    videoElement.play()
    videoElement.addEventListener('canplay', (e) => {
      const canvas = document.getElementById('canvas');
      const ctx = canvas.getContext('2d');
      setInterval(async () => {
        const predictions = await model.estimateFaces({
          input: videoElement
        });
        const keypoints = predictions[0].scaledMesh;
        const min = { x: null, y: null }
        const max = { x: null, y: null };
        [226, 225, 224, 221, 245, 232, 229].forEach(keypointIndex => {
          const [x, y, z] = keypoints[keypointIndex];
          min.x = min.x && min.x < x ? min.x : x
          min.y = min.y && min.y < y ? min.y : y
          max.x = max.x && max.x > x ? max.x : x
          max.y = max.y && max.y > y ? max.y : y
        })
        const width = max.x - min.x
        const height = max.y - min.y
        ctx.drawImage(videoElement, min.x, min.y, width, height, 10, 10, width, height)
      }, 1000 / 60)
    }, false)
  }, false)
})();
