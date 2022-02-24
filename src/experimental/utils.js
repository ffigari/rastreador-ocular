export const setUpInputVideo = async () => {
  const videoElement = document.getElementById("webcam-video");
  const videoCanvasElement = document.getElementById("webcam-canvas");
  videoElement.srcObject = await navigator.mediaDevices.getUserMedia({
    video: {
      width: { min: 320, ideal: 640, max: 1920 },
      height: { min: 240, ideal: 480, max: 1080 },
      facingMode: "user"
    }
  });
  await new Promise((res) => {
    const setUpCanvas = () => {
      videoCanvasElement.width = videoElement.videoWidth;
      videoCanvasElement.height = videoElement.videoHeight;

      videoElement.removeEventListener('timeupdate', setUpCanvas)
      res();
    }
    videoElement.addEventListener('timeupdate', setUpCanvas)
  })
  return { videoCanvasElement, videoElement };
}
