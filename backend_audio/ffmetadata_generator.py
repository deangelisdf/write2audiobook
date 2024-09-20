#!/usr/bin/python3
__doc__ = """
Goal: generate metadata to inject in m4b format file
"""
import audio_metadata

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
    starttimes=[]
    if chapter_titles is None:
        chapter_titles = []
    time = 0 #cummulative start time (nanoseconds)
    for audio_path in input_audio_paths:
        metadata_audio : audio_metadata.formats.mp3.MP3 = audio_metadata.load(audio_path)
        duration_audio : float = metadata_audio.streaminfo.duration*1e9
        time += duration_audio
        starttimes.append(str(int(time)))
    # https://ffmpeg.org/ffmpeg-formats.html#Metadata-1
    # "If the timebase is missing then start/end times are assumed to be in 𝗻𝗮𝗻𝗼𝘀𝗲𝗰𝗼𝗻𝗱𝘀."
    # "chapter start and end times in form ‘START=num’, ‘END=num’, where num is a 𝗽𝗼𝘀𝗶𝘁𝗶𝘃𝗲 𝗶𝗻𝘁𝗲𝗴𝗲𝗿."
    metadata = ""
    if author or title:
        metadata = ";FFMETADATA1"
        if author:
            metadata = f"{metadata}\nartist={author}"
        if title:
            metadata = f"{metadata}\ntitle={title}"
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
