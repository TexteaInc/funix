const FunixRecorder = class {
  private audioMediaRecorder: MediaRecorder | null = null;
  private videoMediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private videoChunks: Blob[] = [];

  constructor() {
    this.audioMediaRecorder = null;
    this.videoMediaRecorder = null;
    this.audioChunks = [];
    this.videoChunks = [];
  }

  public audioRecord = (callback: (file: File) => void) => {
    navigator.mediaDevices
      .getUserMedia({
        audio: true,
        video: false,
      })
      .then((stream) => {
        this.audioMediaRecorder = new MediaRecorder(stream);
        this.audioMediaRecorder.ondataavailable = (e) => {
          this.audioChunks.push(e.data);
        };
        this.audioMediaRecorder.onstop = () => {
          const blob = new Blob(this.audioChunks, {
            type: "audio/ogg",
          });
          this.audioChunks = [];
          const now = new Date().getTime();
          const file = new File([blob], `audio-${now}.ogg`, {
            type: "audio/ogg",
            lastModified: now,
          });
          callback(file);
        };
        const element = document.getElementById("audioRecord");

        if (element !== null) {
          element.addEventListener("click", () => {
            if (this.audioMediaRecorder !== null) {
              this.audioMediaRecorder.stop();
            }
          });
        }

        this.audioMediaRecorder.start();
      });
  };

  public videoRecord = (callback: (file: File) => void, withAudio: boolean) => {
    navigator.mediaDevices
      .getUserMedia({ audio: withAudio, video: true })
      .then((stream) => {
        this.videoMediaRecorder = new MediaRecorder(stream);
        this.videoMediaRecorder.ondataavailable = (e) => {
          this.videoChunks.push(e.data);
        };
        this.videoMediaRecorder.onstop = () => {
          const blob = new Blob(this.videoChunks, {
            type: "video/webm",
          });
          this.videoChunks = [];
          const now = new Date().getTime();
          const file = new File([blob], `video-${now}.webm`, {
            type: "video/webm",
            lastModified: now,
          });
          callback(file);
        };
        const element = document.getElementById("videoRecord");

        if (element !== null) {
          element.addEventListener("click", () => {
            if (this.videoMediaRecorder !== null) {
              this.videoMediaRecorder.stop();
            }
          });
        }

        this.videoMediaRecorder.start();
      });
  };
};

export default FunixRecorder;
