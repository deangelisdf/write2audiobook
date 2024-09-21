#!/usr/bin/python3
__doc__ = """
Goal: generate metadata to inject in m4b format file
"""
from tinytag import TinyTag

def __get_ffmetadata1(**kwargs) -> str:
    isok = (kwargs['title'] is not None) or (kwargs['author'] is not None)
    metadata = ""
    if isok:
        metadata = ";FFMETADATA1"
        if kwargs['author']:
            metadata = f"{metadata}\nartist={kwargs['author']}"
        if kwargs['title']:
            metadata = f"{metadata}\ntitle={kwargs['title']}"
    return metadata

def __get_track_times(input_audio_paths:list) -> list:
    starttimes = []
    time = 0 #cummulative start time (nanoseconds)
    for audio_path in input_audio_paths:
        tag = TinyTag.get(audio_path)
        duration_audio : float = tag.duration*1e9
        time += duration_audio
        starttimes.append(str(int(time)))
    return starttimes

def generate_ffmetadata(input_audio_paths:list,
                        chapter_titles:list=None,
                        author:str=None,
                        title:str=None) -> str:
    """Generate metadata in ffmpeg format.

    Arguments:
        input_audio_paths: List[str] - path of audiable files
        chapter_titles:    List[str] - name of chapters defined on each files

    Returns:
        metadata: str
    """
    starttimes=__get_track_times(input_audio_paths)
    if chapter_titles is None:
        chapter_titles = []
    # https://ffmpeg.org/ffmpeg-formats.html#Metadata-1
    # "If the timebase is missing then start/end times are assumed to be in 𝗻𝗮𝗻𝗼𝘀𝗲𝗰𝗼𝗻𝗱𝘀."
    # "chapter start and end times in form ‘START=num’, ‘END=num’, where num is a 𝗽𝗼𝘀𝗶𝘁𝗶𝘃𝗲 𝗶𝗻𝘁𝗲𝗴𝗲𝗿."
    metadata = __get_ffmetadata1(author=author, title=title)
    last_end = 0
    for idx, start_time in enumerate(starttimes):
        metadata += f"[CHAPTER]\nSTART={last_end}\nEND={start_time}\n"
        if len(chapter_titles) == 0:
            metadata += f"title=c{idx}\n"
        else:
            metadata += f"title={chapter_titles[idx]}\n"
        last_end = start_time
    return metadata

__author__ = "de angelis domenico francesco"
