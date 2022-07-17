import moviepy
from pathlib import Path
from pytube import YouTube
import moviepy.editor as me

def download_video(url):

    my_video = YouTube(url)
    print("********************Download video*************************")
   
    my_video = my_video.streams.get_highest_resolution()
    downloaded_path = my_video.download('/home/kyraneth/projects/ytdownloader/videos')
    return downloaded_path

def cut_video(path,i:int,o:int):
    p= Path(path)
    name = p.stem
    vid = me.VideoFileClip(path)
    vid = vid.subclip(i,o)
    vid.write_videofile('/home/kyraneth/projects/ytdownloader/videos/'+name + '_' +str(i) + '_'+  str(o) + '.mp4')


if __name__ == "__main__":

    path = download_video(
        "https://www.youtube.com/watch?v=PQANZXNuBAI"
    ) 
    

    cut_video(path, 95, 115)

    p=Path(path)
    p.unlink()

