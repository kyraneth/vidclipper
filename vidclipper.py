import moviepy
import argparse
from pathlib import Path
from pytube import YouTube
import moviepy.editor as me
from moviepy.editor import *

my_parser = argparse.ArgumentParser(prog='vidclipper',
                                    description='Download and Clip a Video File')
my_parser.add_argument('url',
                       metavar='url',
                       type=str,
                       help='The URL to the video')
                       
my_parser.add_argument('timecodes',
                       type=float,
                       nargs='*',
                       help='Input ins and outs of video')

my_parser.add_argument('--speed',
                       metavar='speed',
                       type=float,
                       help='Change video speed',
                       default= 1)


my_parser.add_argument('--conc', action='store_true', help='concatenate clipped segments')





def download_video(url):

    my_video = YouTube(url)
    print("********************Download video*************************")
   
    my_video = my_video.streams.get_highest_resolution()
    downloaded_path = my_video.download('/home/kyraneth/projects/ytdownloader/videos')
    return downloaded_path

def cut_video(path,i:int,o:int,conc,speed):
    p= Path(path)
    name = p.stem
    vid = me.VideoFileClip(path)
    vid = vid.without_audio()
    vid = vid.subclip(i,o)
    if speed != '1':
        vid = vid.fx(vfx.speedx, speed)

    if not conc:
        vid.write_videofile('/home/kyraneth/projects/ytdownloader/videos/'+name + '_' +str(i) + '_'+  str(o) + '.mp4')
    return vid




if __name__ == "__main__":
 
    args = my_parser.parse_args()

    url = args.url
    
    input = args.timecodes

    conc = args.conc

    speed = args.speed

    path = download_video(
        url
    ) 

    vid = []
    
    for i in range(0, len(input)-1, 2):

        vid_temp = cut_video(path, input[i], input[i+1],conc, speed)
        vid.append(vid_temp)


    if conc:

        final = me.concatenate_videoclips(vid)

        p= Path(path)
        name = p.stem

        final.write_videofile('/home/kyraneth/projects/ytdownloader/videos/'+name + '_' + 'conc.mp4')


        

    p=Path(path)
    p.unlink()

