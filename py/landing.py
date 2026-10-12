"""Landing page: logo + 30-second advertisement video."""
from pyscript import document, when


@when("ended", "#ad")                      # event: the video finished playing
def video_done(event):
    document.getElementById("enter").classList.add("pulse")
    document.getElementById("adnote").innerText = "Thanks for watching!"


@when("error", "#adsrc")                   # event: the video file was not found
def video_missing(event):
    document.getElementById("adnote").innerText = (
        "Video not found. Put your 30-second ad at assets/chargehub-ad.mp4")
